# -*- coding: utf-8 -*-
"""个性定制看盘 Sheet：用户自选股 + 自定义显示列 + 预警监控

用户在 Excel 的"个性定制看盘" Sheet 中：
  - A-M 列：填写自选股代码（程序自动刷新行情数据）
  - N-Q 列：填写预警条件（涨跌幅下限/上限、价格下限/上限）

达到预警条件时：整行变红 + 弹窗提醒
"""
import logging
from typing import List, Optional

import pandas as pd

from excel_monitor.sheets.base import BaseSheet
from excel_monitor.config_loader import AppConfig
from excel_monitor.core.alert_checker import (
    AlertCondition, AlertChecker
)

# qstock 返回的列名可能不统一，这里做兼容映射
_PRICE_COLS = ["最新", "最新价", "当前价", "现价"]
_CHANGE_COLS = ["涨跌幅", "涨幅", "涨跌幅%"]


class CustomWatchSheet(BaseSheet):
    """个性定制看盘 Sheet Handler"""

    def __init__(self, name, excel_mgr, data_provider, config=None):
        super().__init__(name, excel_mgr, data_provider)
        self.config = config or AppConfig()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._stock_codes: list = []
        self._alert_conditions: List[AlertCondition] = []
        # 数据列数（用于写入时只清除数据区域，保留预警条件列）
        self._data_col_count = len(self.config.custom_watch_columns)
        # 刷新计数器（用于定时重载配置）
        self._refresh_count = 0

    def init(self):
        """从 Excel 读取自选股代码和预警条件（首次加载）"""
        self._reload_from_excel()

    def _reload_from_excel(self):
        """从 Excel 重新读取自选股代码和预警条件"""
        df, _, _ = self.excel_mgr.sheet_to_df(self.sheet)

        if not df.empty and "代码" in df.columns:
            self._stock_codes = df["代码"].dropna().tolist()
            self._logger.info(f"定制自选股加载: {self._stock_codes}")
        else:
            self._stock_codes = self.config.watch_stocks
            self._logger.info(f"使用默认自选股: {self._stock_codes}")

        # 读取预警条件
        self._alert_conditions = self._parse_alert_conditions(df)
        if self._alert_conditions:
            self._logger.info(
                f"预警条件加载: {len(self._alert_conditions)} 只股票"
            )

    def _parse_alert_conditions(self, df: pd.DataFrame) -> List[AlertCondition]:
        """从 DataFrame 解析预警条件"""
        conditions = []
        if df.empty:
            return conditions

        # 获取预警列名
        alert_cols = self.config.alert_columns
        # 找到各预警列在 df 中的位置
        col_map = {}
        for ac in alert_cols:
            if ac in df.columns:
                col_map[ac] = df.columns.get_loc(ac)

        if not col_map:
            return conditions

        for _, row in df.iterrows():
            code = str(row.get("代码", "")).strip()
            if not code or code == "nan":
                continue
            name = str(row.get("名称", code)).strip()

            def _get_val(col_name):
                """安全获取数值，空值返回 None"""
                if col_name not in col_map:
                    return None
                val = row.iloc[col_map[col_name]]
                if pd.isna(val) or val is None:
                    return None
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return None

            cond = AlertCondition(
                code=code,
                name=name,
                change_pct_min=_get_val("涨跌幅下限"),
                change_pct_max=_get_val("涨跌幅上限"),
                price_min=_get_val("价格下限"),
                price_max=_get_val("价格上限"),
            )
            # 至少有一个条件才加入
            if any([cond.change_pct_min, cond.change_pct_max,
                    cond.price_min, cond.price_max]):
                conditions.append(cond)

        return conditions

    @staticmethod
    def _find_value(row, possible_cols: List[str]) -> Optional[float]:
        """从多个可能的列名中找到数值"""
        for col in possible_cols:
            if col in row.index:
                val = row[col]
                if pd.notna(val) and val is not None:
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        pass
        return None

    def refresh(self):
        """刷新定制看盘数据 + 检查预警"""
        self._logger.info("刷新个性定制看盘...")

        # 每隔 N 次刷新，重新从 Excel 读取股票代码和预警条件（支持实时修改）
        self._refresh_count += 1
        reload_interval = self.config.config_reload_interval
        if reload_interval > 0 and self._refresh_count % reload_interval == 0:
            self._logger.info(f"第 {self._refresh_count} 次刷新，重载 Excel 配置...")
            self._reload_from_excel()

        if not self._stock_codes:
            self._logger.warning("无自选股，跳过刷新")
            return

        # 获取实时行情
        df_rt = self.data.get_stock_realtime(self._stock_codes)
        if df_rt.empty:
            return

        # 按配置列过滤
        df_display = self.data.filter_columns(
            df_rt, self.config.custom_watch_columns
        )

        # 补充刷新时间
        if "刷新时间" in self.config.custom_watch_columns \
                and "刷新时间" not in df_display.columns:
            if "时间" in df_rt.columns:
                df_display["刷新时间"] = df_rt["时间"]

        # 写入数据（只清除数据列区域，保留预警条件列）
        self._write_data(df_display)

        # 检查预警并高亮
        triggered_rows = self._check_and_highlight(df_display, df_rt)

        # 弹窗提醒
        if triggered_rows and self.config.alert_popup_enabled:
            self._show_popup(triggered_rows)

    def _write_data(self, df: pd.DataFrame):
        """写入数据到 Sheet（只清除数据列，不触碰预警条件列）"""
        if self.sheet is None:
            return
        # 只清除数据列区域（列 1 到 data_col_count）
        self.excel_mgr.clear_range(
            self.sheet, start_row=1, start_col=1,
            end_row=200, end_col=self._data_col_count
        )
        self.excel_mgr.write_df(self.sheet, df, start_row=1, start_col=1)

    def _check_and_highlight(self, df_display: pd.DataFrame,
                             df_rt: pd.DataFrame) -> List:
        """检查预警条件，高亮触发的行，返回触发的 AlertResult 列表"""
        if not self._alert_conditions:
            return []

        # 清除之前的高亮
        total_cols = self._data_col_count + len(self.config.alert_columns)
        self.excel_mgr.clear_highlight(
            self.sheet, start_row=2, end_row=200,
            start_col=1, end_col=total_cols
        )

        # 构建 code -> price / change_pct 映射
        price_map = {}
        change_map = {}
        for _, row in df_rt.iterrows():
            code = str(row.get("代码", "")).strip()
            if not code:
                continue
            price = self._find_value(row, _PRICE_COLS)
            change = self._find_value(row, _CHANGE_COLS)
            if price is not None:
                price_map[code] = price
            if change is not None:
                change_map[code] = change

        # 批量检查预警
        all_results = AlertChecker.check_batch(
            self._alert_conditions, price_map, change_map
        )

        if not all_results:
            return []

        # 找出触发的股票代码
        triggered_codes = {r.code for r in all_results}

        # 高亮触发的行（Excel 行号 = 数据行 + 1（表头）+ 1（从1开始））
        for idx, row in df_display.iterrows():
            code = str(row.get("代码", "")).strip()
            if code in triggered_codes:
                excel_row = idx + 2  # df 索引 0 = Excel 第 2 行
                self.excel_mgr.highlight_row(
                    self.sheet, row=excel_row,
                    start_col=1, end_col=total_cols,
                    color=(255, 200, 200)
                )
                self._logger.warning(
                    f"预警触发: {code} 行 {excel_row} 已高亮"
                )

        return all_results

    def _show_popup(self, results: List):
        """弹出预警提醒窗口"""
        message = AlertChecker.format_alert_message(results)
        self._logger.warning(f"预警弹窗:\n{message}")

        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning("盯盘预警", message)
            root.destroy()
        except Exception as e:
            # 无 GUI 环境（如 CI/服务器），降级为日志输出
            self._logger.info(f"无 GUI 环境，预警仅记录日志: {e}")
