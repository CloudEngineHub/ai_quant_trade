# -*- coding: utf-8 -*-
"""Sheet Handler 逻辑测试（mock 数据源）"""
import pandas as pd
from unittest.mock import MagicMock

from excel_monitor.config_loader import AppConfig
from excel_monitor.core.data_provider import DataProvider
from excel_monitor.sheets.market_overview import MarketOverviewSheet
from excel_monitor.sheets.detailed_quotes import DetailedQuotesSheet
from excel_monitor.sheets.news_sheet import NewsSheet
from excel_monitor.sheets.custom_watch import CustomWatchSheet


def test_market_overview_refresh_with_mock():
    """测试大盘 Sheet 刷新逻辑（mock 数据源）"""
    mock_excel = MagicMock()
    mock_data = MagicMock()

    mock_data.get_index_realtime.return_value = pd.DataFrame({
        "名称": ["上证指数", "深证成指"],
        "最新": [3200.0, 10500.0],
        "涨幅": [0.5, -0.3],
    })
    mock_data.get_industry_boards.return_value = pd.DataFrame({
        "名称": ["银行", "证券"], "涨幅": [1.2, -0.5],
    })
    mock_data.get_concept_boards.return_value = pd.DataFrame()
    mock_data.get_limit_up_pool.return_value = pd.DataFrame()

    sheet = MarketOverviewSheet("大盘", mock_excel, mock_data)
    sheet.sheet = MagicMock()

    sheet.refresh()

    mock_data.get_index_realtime.assert_called_once()
    mock_data.get_industry_boards.assert_called_once()


def test_detailed_quotes_refresh_with_mock():
    """测试详细行情 Sheet 刷新逻辑"""
    mock_excel = MagicMock()
    mock_data = MagicMock()

    mock_excel.sheet_to_df.return_value = (
        pd.DataFrame({
            "代码": ["000001", "600000"],
            "名称": ["平安银行", "浦发银行"],
        }),
        3, 2,
    )
    mock_data.get_stock_realtime.return_value = pd.DataFrame({
        "代码": ["000001", "600000"],
        "名称": ["平安银行", "浦发银行"],
        "最新": [10.5, 8.3],
        "涨幅": [2.1, -0.5],
        "时间": ["10:30:00", "10:30:00"],
    })
    mock_data.get_billboard.return_value = pd.DataFrame()
    mock_data.get_realtime_change.return_value = pd.DataFrame()

    sheet = DetailedQuotesSheet("详细行情", mock_excel, mock_data)
    sheet.sheet = MagicMock()

    sheet.init()
    sheet.refresh()

    mock_data.get_stock_realtime.assert_called_once()


def test_news_sheet_refresh_with_mock():
    """测试新闻 Sheet 刷新逻辑"""
    mock_excel = MagicMock()
    mock_data = MagicMock()

    mock_data.get_news_cls.return_value = pd.DataFrame({
        "发布时间": ["10:30", "10:25"],
        "标题": ["央行降息", "GDP增长5%"],
    })
    mock_data.get_news_js.return_value = pd.DataFrame({
        "时间": ["10:28"],
        "内容": ["美国CPI数据公布"],
    })

    sheet = NewsSheet("新闻", mock_excel, mock_data)
    sheet.sheet = MagicMock()

    sheet.refresh()

    mock_data.get_news_cls.assert_called_once()
    mock_data.get_news_js.assert_called_once()


def test_custom_watch_refresh_with_mock():
    """测试个性定制看盘 Sheet 刷新逻辑（无预警条件）"""
    mock_excel = MagicMock()
    real_dp = DataProvider()
    mock_data = MagicMock(wraps=real_dp)

    mock_excel.sheet_to_df.return_value = (
        pd.DataFrame({
            "代码": ["中国平安", "贵州茅台"],
            "名称": ["中国平安", "贵州茅台"],
        }),
        3, 2,
    )
    mock_data.get_stock_realtime.return_value = pd.DataFrame({
        "代码": ["中国平安", "贵州茅台"],
        "名称": ["中国平安", "贵州茅台"],
        "最新": [45.0, 1800.0],
        "涨幅": [1.5, 0.8],
        "时间": ["10:30:00", "10:30:00"],
    })

    config = AppConfig()
    sheet = CustomWatchSheet("个性定制看盘", mock_excel, mock_data, config)
    sheet.sheet = MagicMock()

    sheet.init()
    sheet.refresh()

    mock_data.get_stock_realtime.assert_called_once()
    # 无预警条件，不应高亮
    mock_excel.highlight_row.assert_not_called()


def test_custom_watch_alert_triggered():
    """测试预警触发：涨跌幅超限 → 高亮 + 弹窗"""
    mock_excel = MagicMock()
    real_dp = DataProvider()
    mock_data = MagicMock(wraps=real_dp)

    # Excel 中有预警条件：中国平安 涨跌幅上限 3%
    mock_excel.sheet_to_df.return_value = (
        pd.DataFrame({
            "代码": ["中国平安", "贵州茅台"],
            "名称": ["中国平安", "贵州茅台"],
            "涨跌幅下限": [None, None],
            "涨跌幅上限": [3.0, None],
            "价格下限": [None, None],
            "价格上限": [None, None],
        }),
        3, 6,
    )
    # 实时行情：中国平安涨 5%（超限），贵州茅台涨 0.8%（正常）
    mock_data.get_stock_realtime.return_value = pd.DataFrame({
        "代码": ["中国平安", "贵州茅台"],
        "名称": ["中国平安", "贵州茅台"],
        "最新": [45.0, 1800.0],
        "涨幅": [5.0, 0.8],
        "时间": ["10:30:00", "10:30:00"],
    })

    config = AppConfig()
    config.alert_popup_enabled = False  # 测试中禁用弹窗
    sheet = CustomWatchSheet("个性定制看盘", mock_excel, mock_data, config)
    sheet.sheet = MagicMock()

    sheet.init()
    sheet.refresh()

    # 验证预警条件被加载
    assert len(sheet._alert_conditions) == 1
    assert sheet._alert_conditions[0].code == "中国平安"

    # 验证高亮被调用（至少 1 次：中国平安）
    assert mock_excel.highlight_row.call_count >= 1

    # 验证清除高亮也被调用（每次刷新前清除旧高亮）
    mock_excel.clear_highlight.assert_called_once()


def test_custom_watch_alert_price_triggered():
    """测试价格预警触发"""
    mock_excel = MagicMock()
    real_dp = DataProvider()
    mock_data = MagicMock(wraps=real_dp)

    mock_excel.sheet_to_df.return_value = (
        pd.DataFrame({
            "代码": ["贵州茅台"],
            "名称": ["贵州茅台"],
            "涨跌幅下限": [None],
            "涨跌幅上限": [None],
            "价格下限": [None],
            "价格上限": [2000.0],
        }),
        2, 6,
    )
    # 茅台价格 2100，超过 2000 上限
    mock_data.get_stock_realtime.return_value = pd.DataFrame({
        "代码": ["贵州茅台"],
        "名称": ["贵州茅台"],
        "最新": [2100.0],
        "涨幅": [1.0],
        "时间": ["10:30:00"],
    })

    config = AppConfig()
    config.alert_popup_enabled = False
    sheet = CustomWatchSheet("个性定制看盘", mock_excel, mock_data, config)
    sheet.sheet = MagicMock()

    sheet.init()
    sheet.refresh()

    assert len(sheet._alert_conditions) == 1
    assert mock_excel.highlight_row.call_count == 1


def test_custom_watch_no_alert_when_within_range():
    """测试未触发预警：行情在条件范围内"""
    mock_excel = MagicMock()
    real_dp = DataProvider()
    mock_data = MagicMock(wraps=real_dp)

    mock_excel.sheet_to_df.return_value = (
        pd.DataFrame({
            "代码": ["中国平安"],
            "名称": ["中国平安"],
            "涨跌幅下限": [-3.0],
            "涨跌幅上限": [5.0],
            "价格下限": [40.0],
            "价格上限": [50.0],
        }),
        2, 6,
    )
    # 涨跌幅 1%，价格 45 → 都在范围内
    mock_data.get_stock_realtime.return_value = pd.DataFrame({
        "代码": ["中国平安"],
        "名称": ["中国平安"],
        "最新": [45.0],
        "涨幅": [1.0],
        "时间": ["10:30:00"],
    })

    config = AppConfig()
    config.alert_popup_enabled = False
    sheet = CustomWatchSheet("个性定制看盘", mock_excel, mock_data, config)
    sheet.sheet = MagicMock()

    sheet.init()
    sheet.refresh()

    # 有预警条件但未触发
    assert len(sheet._alert_conditions) == 1
    mock_excel.highlight_row.assert_not_called()
