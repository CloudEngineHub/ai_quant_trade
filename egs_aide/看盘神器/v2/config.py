# -*- coding: utf-8 -*-
"""盯盘工具 V2 配置模块"""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SheetConfig:
    """Sheet 名称映射"""
    market_overview: str = "大盘"
    detailed_quotes: str = "详细行情"
    news: str = "新闻"
    custom_watch: str = "个性定制看盘"


@dataclass
class AppConfig:
    """全局配置"""
    # Excel 模板文件名
    excel_template: str = "看盘模板.xlsx"

    # 刷新间隔（秒）
    refresh_interval: int = 3

    # Sheet 名称映射
    sheets: Dict[str, str] = field(default_factory=lambda: {
        "market_overview": "大盘",
        "detailed_quotes": "详细行情",
        "news": "新闻",
        "custom_watch": "个性定制看盘",
    })

    # 大盘指数列表（qstock 简称）
    market_indices: List[str] = field(default_factory=lambda: [
        "上证指数", "深证成指", "创业板指", "沪深300",
        "上证50", "中证500", "科创50",
    ])

    # 自选股代码列表（用户可修改）
    watch_stocks: List[str] = field(default_factory=lambda: [
        "中国平安", "贵州茅台", "宁德时代", "比亚迪",
        "招商银行", "东方财富",
    ])

    # 个性定制看盘显示列
    custom_watch_columns: List[str] = field(default_factory=lambda: [
        "代码", "名称", "最新价", "涨跌幅", "涨跌额",
        "成交量", "成交额", "换手率", "最高", "最低",
        "开盘", "昨收", "刷新时间",
    ])

    # 新闻显示条数
    news_max_rows: int = 50
