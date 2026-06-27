# -*- coding: utf-8 -*-
"""数据提供者：封装多数据源获取 + 统一异常处理 + fallback 机制

主数据源：qstock（基于东方财富、同花顺免费接口）
备选数据源：AKShare / 东方财富 / 腾讯 / 网易 / efinance（参考 egs_data/）

调用规则：
    1. 主源优先：先尝试 qstock
    2. 自动 fallback：主源失败或返回空时，按 fallback_chain 依次尝试备选源
    3. 单点失败不影响整体：每个方法独立 try-except，最终失败返回空 DataFrame
    4. 备选源默认启用：可通过 AppConfig.enabled_backup_sources 关闭某些源
"""
import logging
import traceback
from typing import List, Dict, Callable, Optional

import pandas as pd

from excel_monitor.core.backup_sources import BackupSources


def _get_qstock():
    """延迟导入 qstock（避免 import 时触发网络请求）"""
    import qstock as qs
    return qs


class DataProvider:
    """多源数据获取封装

    Attributes:
        backup: 备选数据源集合（BackupSources 实例）
        enabled_sources: 启用的备选源名称列表（按优先级排序）
    """

    def __init__(self, config=None):
        self._logger = logging.getLogger(self.__class__.__name__)
        # config 可为 AppConfig，从中读取 enabled_backup_sources
        self._config = config
        enabled = None
        if config is not None and hasattr(config, "enabled_backup_sources"):
            enabled = list(getattr(config, "enabled_backup_sources"))
        self.backup = BackupSources(config)
        # 默认全部启用；用户可在 config 中关闭某个源
        self.enabled_sources = enabled or [
            "akshare", "eastmoney", "tencent", "netease", "efinance",
        ]

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

    # ===== Fallback 公共方法 =====

    def _try_with_fallback(self, primary_func: Callable,
                           fallback_chain: List[tuple],
                           args: tuple, name: str,
                           kwargs: Optional[dict] = None) -> pd.DataFrame:
        """主源 + 备选源依次尝试

        Args:
            primary_func: 主源函数（qstock）
            fallback_chain: [(源名, 源方法), ...] 按优先级排序
            args: 位置参数
            name: 数据名（用于日志）
            kwargs: 关键字参数

        Returns:
            DataFrame（成功）或空 DataFrame（全部失败）
        """
        kwargs = kwargs or {}

        # 1. 尝试主源
        try:
            df = primary_func(*args, **kwargs)
            if df is not None and not df.empty:
                return df
            self._logger.debug(f"主源(qstock) 获取 {name} 返回空，尝试备选源")
        except Exception as e:
            self._logger.warning(f"主源(qstock) 获取 {name} 失败: {e}")

        # 2. 依次尝试启用的备选源
        for source_name, source_method in fallback_chain:
            if source_name not in self.enabled_sources:
                continue
            try:
                df = source_method(*args, **kwargs)
                if df is not None and not df.empty:
                    self._logger.info(f"备选源[{source_name}] 成功获取 {name}")
                    return df
            except Exception as e:
                self._logger.warning(
                    f"备选源[{source_name}] 获取 {name} 失败: {e}"
                )

        self._logger.error(f"所有数据源获取 {name} 均失败")
        return pd.DataFrame()

    # ===== 数据获取方法（qstock + 多源 fallback） =====

    def _qstock_index_realtime(self, code_list: List[str]) -> pd.DataFrame:
        qs = _get_qstock()
        df = qs.realtime_data(code=code_list)
        return df if df is not None and not df.empty else pd.DataFrame()

    def get_index_realtime(self, code_list: List[str]) -> pd.DataFrame:
        """获取指数实时行情（主源 qstock → 备选 akshare）"""
        return self._try_with_fallback(
            primary_func=self._qstock_index_realtime,
            fallback_chain=[("akshare", self.backup.akshare_index_realtime)],
            args=(code_list,),
            name="指数行情",
        )

    def _qstock_stock_realtime(self, code_list: List[str]) -> pd.DataFrame:
        qs = _get_qstock()
        clean_codes = [self.clean_code(c) for c in code_list]
        df = qs.realtime_data(code=clean_codes)
        return df if df is not None and not df.empty else pd.DataFrame()

    def get_stock_realtime(self, code_list: List[str]) -> pd.DataFrame:
        """获取个股实时行情
        fallback 链：qstock → akshare → tencent → eastmoney → efinance
        """
        return self._try_with_fallback(
            primary_func=self._qstock_stock_realtime,
            fallback_chain=[
                ("akshare", self.backup.akshare_stock_realtime),
                ("tencent", self.backup.tencent_stock_realtime),
                ("eastmoney", self.backup.eastmoney_stock_realtime),
                ("efinance", self.backup.efinance_stock_realtime),
            ],
            args=(code_list,),
            name="个股行情",
        )

    def get_industry_boards(self) -> pd.DataFrame:
        """获取行业板块行情

        qstock 较稳定，仅 akshare 作为 fallback（其他源格式不统一）
        """
        try:
            qs = _get_qstock()
            df = qs.realtime_data("行业板块")
            if df is not None and not df.empty:
                return df
        except Exception as e:
            self._logger.warning(f"主源(qstock) 获取行业板块失败: {e}")
        # fallback: akshare 行业板块
        if "akshare" in self.enabled_sources:
            try:
                df = self._akshare_industry_boards()
                if df is not None and not df.empty:
                    self._logger.info("备选源[akshare] 成功获取 行业板块")
                    return df
            except Exception as e:
                self._logger.warning(f"备选源[akshare] 获取行业板块失败: {e}")
        return pd.DataFrame()

    def _akshare_industry_boards(self) -> pd.DataFrame:
        """AKShare: 行业板块行情（fallback）"""
        ak = self.backup._get_akshare()
        df = ak.stock_board_industry_name_em()
        if df is None or df.empty:
            return pd.DataFrame()
        rename = {
            "板块名称": "名称", "最新价": "最新", "涨跌幅": "涨幅",
            "总市值": "总市值", "换手率": "换手率",
            "上涨家数": "上涨家数", "下跌家数": "下跌家数",
            "领涨股票": "领涨股票", "领涨股票-涨跌幅": "领涨涨幅",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
        return df.reset_index(drop=True)

    def get_concept_boards(self) -> pd.DataFrame:
        """获取概念板块行情"""
        try:
            qs = _get_qstock()
            df = qs.realtime_data("概念板块")
            if df is not None and not df.empty:
                return df
        except Exception as e:
            self._logger.warning(f"主源(qstock) 获取概念板块失败: {e}")
        if "akshare" in self.enabled_sources:
            try:
                df = self._akshare_concept_boards()
                if df is not None and not df.empty:
                    self._logger.info("备选源[akshare] 成功获取 概念板块")
                    return df
            except Exception as e:
                self._logger.warning(f"备选源[akshare] 获取概念板块失败: {e}")
        return pd.DataFrame()

    def _akshare_concept_boards(self) -> pd.DataFrame:
        """AKShare: 概念板块行情（fallback）"""
        ak = self.backup._get_akshare()
        df = ak.stock_board_concept_name_em()
        if df is None or df.empty:
            return pd.DataFrame()
        rename = {
            "板块名称": "名称", "最新价": "最新", "涨跌幅": "涨幅",
            "总市值": "总市值", "换手率": "换手率",
            "上涨家数": "上涨家数", "下跌家数": "下跌家数",
            "领涨股票": "领涨股票", "领涨股票-涨跌幅": "领涨涨幅",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
        return df.reset_index(drop=True)

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

    # ===== 新闻类（多源 fallback） =====

    def _qstock_news_cls(self) -> pd.DataFrame:
        qs = _get_qstock()
        df = qs.news_data()
        if df is not None and not df.empty:
            df["发布时间"] = df["发布时间"].apply(str)
            df["发布日期"] = df["发布日期"].apply(str)
        return df if df is not None and not df.empty else pd.DataFrame()

    def get_news_cls(self) -> pd.DataFrame:
        """获取财联社电报
        fallback 链：qstock → akshare
        """
        return self._try_with_fallback(
            primary_func=self._qstock_news_cls,
            fallback_chain=[("akshare", self.backup.akshare_news_cls)],
            args=(),
            name="财联社电报",
        )

    def _qstock_news_js(self) -> pd.DataFrame:
        qs = _get_qstock()
        df = qs.news_data("js")
        return df if df is not None and not df.empty else pd.DataFrame()

    def get_news_js(self) -> pd.DataFrame:
        """获取市场快讯（金十数据 → 东方财富全球快讯 fallback）"""
        return self._try_with_fallback(
            primary_func=self._qstock_news_js,
            fallback_chain=[("akshare", self.backup.akshare_news_js)],
            args=(),
            name="市场快讯",
        )

    def get_stock_news(self, code: str) -> pd.DataFrame:
        """获取个股新闻
        fallback 链：qstock → akshare → eastmoney
        """
        try:
            qs = _get_qstock()
            df = qs.stock_news(code)
            if df is not None and not df.empty:
                return df
        except Exception as e:
            self._logger.warning(f"主源(qstock) 获取个股新闻失败: {e}")
        # akshare fallback
        if "akshare" in self.enabled_sources:
            df = self.backup.akshare_stock_news(code)
            if df is not None and not df.empty:
                self._logger.info(f"备选源[akshare] 成功获取 个股新闻: {code}")
                return df
        # eastmoney fallback
        if "eastmoney" in self.enabled_sources:
            df = self.backup.eastmoney_stock_news(code)
            if df is not None and not df.empty:
                self._logger.info(f"备选源[eastmoney] 成功获取 个股新闻: {code}")
                return df
        return pd.DataFrame()

    # ===== K 线类（多源 fallback） =====

    def _qstock_kline(self, code: str, count: int = 60,
                      freq: str = "d") -> pd.DataFrame:
        qs = _get_qstock()
        df = qs.get_data(code, count=count, freq=freq)
        if df is None or df.empty:
            return pd.DataFrame()
        col_map = {
            "开盘": "Open", "最高": "High", "最低": "Low",
            "收盘": "Close", "成交量": "Volume",
            "open": "Open", "high": "High", "low": "Low",
            "close": "Close", "volume": "Volume",
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        return df

    def get_kline_data(self, code: str, count: int = 60,
                       freq: str = "d") -> pd.DataFrame:
        """获取 K 线历史数据
        fallback 链：qstock → tencent → eastmoney → akshare → efinance → netease

        Args:
            code: 股票代码或名称
            count: K 线数量
            freq: 周期 'd'=日线, 'w'=周线, 'm'=月线

        Returns:
            DataFrame，包含 Open/High/Low/Close/Volume 列，索引为日期
        """
        return self._try_with_fallback(
            primary_func=self._qstock_kline,
            fallback_chain=[
                ("tencent", self.backup.tencent_kline),
                ("eastmoney", self.backup.eastmoney_kline),
                ("akshare", self.backup.akshare_kline),
                ("efinance", self.backup.efinance_kline),
                ("netease", self.backup.netease_kline),
            ],
            args=(code, count, freq),
            name=f"K线({code})",
        )

    # ===== 新增数据类型（无主源 qstock 实现，直接走备选源） =====

    def get_north_money(self) -> pd.DataFrame:
        """获取北向资金每日净流入（akshare 数据源）

        Returns:
            DataFrame：日期、当日净流入、当日余额
        """
        if "akshare" not in self.enabled_sources:
            self._logger.warning("akshare 未启用，无法获取北向资金")
            return pd.DataFrame()
        return self.backup.akshare_north_money()

    def get_stock_money_flow(self, code: str) -> pd.DataFrame:
        """获取个股资金流向（eastmoney 数据源）

        Args:
            code: 股票代码

        Returns:
            DataFrame：日期、主力净流入、小单净流入、中单净流入、大单净流入、超大单净流入
        """
        if "eastmoney" not in self.enabled_sources:
            self._logger.warning("eastmoney 未启用，无法获取资金流向")
            return pd.DataFrame()
        return self.backup.eastmoney_money_flow(code)

    def get_weibo_sentiment(self) -> pd.DataFrame:
        """获取微博舆情报告（akshare 数据源）

        Returns:
            DataFrame：股票代码、股票名称、微博舆情指数、正负面情绪占比
        """
        if "akshare" not in self.enabled_sources:
            self._logger.warning("akshare 未启用，无法获取微博舆情")
            return pd.DataFrame()
        return self.backup.akshare_weibo_sentiment()

    def get_news_sentiment(self) -> pd.DataFrame:
        """获取新闻情绪指数（akshare 数据源）

        Returns:
            DataFrame：日期、新闻情绪指数
        """
        if "akshare" not in self.enabled_sources:
            self._logger.warning("akshare 未启用，无法获取新闻情绪指数")
            return pd.DataFrame()
        return self.backup.akshare_news_sentiment()

    def get_guba_hot_posts(self, page_size: int = 20) -> pd.DataFrame:
        """获取股吧热门帖子（eastmoney 数据源）

        Returns:
            DataFrame：标题、发布时间、阅读量、评论数、点赞数
        """
        if "eastmoney" not in self.enabled_sources:
            self._logger.warning("eastmoney 未启用，无法获取股吧热门")
            return pd.DataFrame()
        return self.backup.eastmoney_guba_hot(page_size)

    def get_guba_posts(self, code: str, page_size: int = 20) -> pd.DataFrame:
        """获取个股股吧帖子（eastmoney 数据源）

        Args:
            code: 股票代码
            page_size: 返回条数

        Returns:
            DataFrame：标题、发布时间、阅读量、评论数、点赞数、来源
        """
        if "eastmoney" not in self.enabled_sources:
            self._logger.warning("eastmoney 未启用，无法获取个股股吧")
            return pd.DataFrame()
        return self.backup.eastmoney_guba_posts(code, page_size)

    def get_global_sina_news(self) -> pd.DataFrame:
        """获取新浪财经全球快讯（akshare 数据源，新增）"""
        if "akshare" not in self.enabled_sources:
            return pd.DataFrame()
        return self.backup.akshare_news_sina()

    def get_caixin_news(self) -> pd.DataFrame:
        """获取财新网主要财经新闻（akshare 数据源，新增）"""
        if "akshare" not in self.enabled_sources:
            return pd.DataFrame()
        return self.backup.akshare_news_caixin()

    def get_cctv_news(self, date_str: Optional[str] = None) -> pd.DataFrame:
        """获取新闻联播文字稿（akshare 数据源，新增）

        Args:
            date_str: 日期 YYYYMMDD，默认今天
        """
        if "akshare" not in self.enabled_sources:
            return pd.DataFrame()
        return self.backup.akshare_news_cctv(date_str)
