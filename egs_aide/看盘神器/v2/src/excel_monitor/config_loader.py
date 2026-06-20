# -*- coding: utf-8 -*-
"""配置加载器：从 YAML 读取配置，返回 AppConfig 对象"""
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

import yaml


@dataclass
class AppConfig:
    """全局配置（带默认值，可被 YAML 覆盖）"""
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

    # 预警条件列名（用户在 Excel 中填写阈值）
    alert_columns: List[str] = field(default_factory=lambda: [
        "涨跌幅下限", "涨跌幅上限", "价格下限", "价格上限",
    ])

    # 是否启用预警弹窗
    alert_popup_enabled: bool = True

    # 新闻显示条数
    news_max_rows: int = 50


def load_config(yaml_path: Optional[str] = None) -> AppConfig:
    """从 YAML 文件加载配置，合并到默认值上

    Args:
        yaml_path: YAML 配置文件路径。为 None 时返回默认配置。

    Returns:
        AppConfig 对象
    """
    if yaml_path is None or not os.path.exists(yaml_path):
        return AppConfig()

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # 用默认值初始化，再用 yaml 数据覆盖
    defaults = asdict(AppConfig())
    defaults.update(data)
    return AppConfig(**defaults)
