# -*- coding: utf-8 -*-
"""数据提供者：封装 qstock 数据获取，统一异常处理"""
import logging
import traceback
from typing import List, Dict, Optional

import pandas as pd


def _get_qstock():
    """延迟导入 qstock（避免 import 时触发网络请求）"""
    import qstock as qs
    return qs


class DataProvider:
    """qstock 数据获取封装"""

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    # ===== 纯逻辑方法（可测试） =====

    @staticmethod
    def clean_code(code: str) -> str:
        """去除代码后缀，如 000001.SZ -> 000001"""
        return code.split(".")[0]

    @staticmethod
    def filter_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """按指定列过滤 DataFrame，仅保留存在的列"""
        existing = [c for c in columns if c in df.columns]
        return df[existing].copy()

    @staticmethod
    def rename_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """重命名列"""
        return df.rename(columns=mapping)

    # ===== 数据获取方法（调用 qstock） =====

    def get_index_realtime(self, code_list: List[str]) -> pd.DataFrame:
        """获取指数实时行情"""
        try:
            qs = _get_qstock()
            df = qs.realtime_data(code=code_list)
            return df if df is not None and not df.empty else pd.DataFrame()
        except Exception as e:
            self._logger.error(f"获取指数行情失败: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_stock_realtime(self, code_list: List[str]) -> pd.DataFrame:
        """获取个股实时行情"""
        try:
            qs = _get_qstock()
            clean_codes = [self.clean_code(c) for c in code_list]
            df = qs.realtime_data(code=clean_codes)
            return df if df is not None and not df.empty else pd.DataFrame()
        except Exception as e:
            self._logger.error(f"获取个股行情失败: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_industry_boards(self) -> pd.DataFrame:
        """获取行业板块行情"""
        try:
            qs = _get_qstock()
            df = qs.realtime_data("行业板块")
            return df if df is not None and not df.empty else pd.DataFrame()
        except Exception as e:
            self._logger.error(f"获取行业板块失败: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_concept_boards(self) -> pd.DataFrame:
        """获取概念板块行情"""
        try:
            qs = _get_qstock()
            df = qs.realtime_data("概念板块")
            return df if df is not None and not df.empty else pd.DataFrame()
        except Exception as e:
            self._logger.error(f"获取概念板块失败: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_limit_up_pool(self) -> pd.DataFrame:
        """获取涨停板"""
        try:
            qs = _get_qstock()
            df = qs.stock_zt_pool()
            return df if df is not None and not df.empty else pd.DataFrame()
        except Exception as e:
            self._logger.error(f"获取涨停板失败: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_billboard(self) -> pd.DataFrame:
        """获取龙虎榜"""
        try:
            qs = _get_qstock()
            df = qs.stock_billboard()
            return df if df is not None and not df.empty else pd.DataFrame()
        except Exception as e:
            self._logger.error(f"获取龙虎榜失败: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_realtime_change(self) -> pd.DataFrame:
        """获取盘口异动"""
        try:
            qs = _get_qstock()
            df = qs.realtime_change()
            return df if df is not None and not df.empty else pd.DataFrame()
        except Exception as e:
            self._logger.error(f"获取盘口异动失败: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_news_cls(self) -> pd.DataFrame:
        """获取财联社电报"""
        try:
            qs = _get_qstock()
            df = qs.news_data()
            if df is not None and not df.empty:
                df["发布时间"] = df["发布时间"].apply(str)
                df["发布日期"] = df["发布日期"].apply(str)
            return df if df is not None and not df.empty else pd.DataFrame()
        except Exception as e:
            self._logger.error(f"获取财联社新闻失败: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_news_js(self) -> pd.DataFrame:
        """获取市场快讯（金十数据）"""
        try:
            qs = _get_qstock()
            df = qs.news_data("js")
            return df if df is not None and not df.empty else pd.DataFrame()
        except Exception as e:
            self._logger.error(f"获取市场快讯失败: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    def get_stock_news(self, code: str) -> pd.DataFrame:
        """获取个股新闻"""
        try:
            qs = _get_qstock()
            df = qs.stock_news(code)
            return df if df is not None and not df.empty else pd.DataFrame()
        except Exception as e:
            self._logger.error(f"获取个股新闻失败: {e}")
            traceback.print_exc()
            return pd.DataFrame()
