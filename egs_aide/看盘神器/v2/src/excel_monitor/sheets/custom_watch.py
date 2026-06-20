# -*- coding: utf-8 -*-
"""个性定制看盘 Sheet：用户自选股 + 自定义显示列"""
import logging

import pandas as pd

from excel_monitor.sheets.base import BaseSheet
from excel_monitor.config_loader import AppConfig


class CustomWatchSheet(BaseSheet):
    """个性定制看盘 Sheet Handler

    用户在 Excel 的"个性定制看盘" Sheet 中填写自选股代码，
    程序读取后获取实时行情并按 config.custom_watch_columns 过滤显示。
    """

    def __init__(self, name, excel_mgr, data_provider, config=None):
        super().__init__(name, excel_mgr, data_provider)
        self.config = config or AppConfig()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._stock_codes: list = []

    def init(self):
        """从 Excel 读取用户自定义的自选股"""
        df, _, _ = self.excel_mgr.sheet_to_df(self.sheet)
        if not df.empty and "代码" in df.columns:
            self._stock_codes = df["代码"].dropna().tolist()
            self._logger.info(f"定制自选股加载: {self._stock_codes}")
        else:
            self._stock_codes = self.config.watch_stocks
            self._logger.info(f"使用默认自选股: {self._stock_codes}")

    def refresh(self):
        """刷新定制看盘数据"""
        self._logger.info("刷新个性定制看盘...")

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

        self._write(df_display, start_row=1, start_col=1)
