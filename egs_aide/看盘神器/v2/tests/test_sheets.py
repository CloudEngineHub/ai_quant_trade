import pandas as pd
from unittest.mock import MagicMock, patch
from config import AppConfig
from sheets.market_overview import MarketOverviewSheet


def test_market_overview_refresh_with_mock():
    """测试大盘 Sheet 刷新逻辑（mock 数据源）"""
    mock_excel = MagicMock()
    mock_data = MagicMock()

    # mock 返回数据
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

    # 不应抛异常
    sheet.refresh()

    # 验证数据源被调用
    mock_data.get_index_realtime.assert_called_once()
    mock_data.get_industry_boards.assert_called_once()


from sheets.detailed_quotes import DetailedQuotesSheet


def test_detailed_quotes_refresh_with_mock():
    """测试详细行情 Sheet 刷新逻辑"""
    mock_excel = MagicMock()
    mock_data = MagicMock()

    # mock Sheet 已有自选股数据
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


from sheets.news_sheet import NewsSheet


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


from sheets.custom_watch import CustomWatchSheet


def test_custom_watch_refresh_with_mock():
    """测试个性定制看盘 Sheet 刷新逻辑"""
    mock_excel = MagicMock()
    mock_data = MagicMock()

    # mock Sheet 中已有自选股
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
