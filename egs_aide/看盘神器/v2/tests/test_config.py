from config import AppConfig, SheetConfig


def test_default_config():
    cfg = AppConfig()
    assert cfg.refresh_interval == 3
    assert cfg.excel_template == "看盘模板.xlsx"
    assert "上证指数" in cfg.market_indices
    assert len(cfg.watch_stocks) > 0


def test_sheet_names():
    cfg = AppConfig()
    assert cfg.sheets["market_overview"] == "大盘"
    assert cfg.sheets["detailed_quotes"] == "详细行情"
    assert cfg.sheets["news"] == "新闻"
    assert cfg.sheets["custom_watch"] == "个性定制看盘"


def test_custom_watch_columns():
    cfg = AppConfig()
    assert "代码" in cfg.custom_watch_columns
    assert "名称" in cfg.custom_watch_columns
