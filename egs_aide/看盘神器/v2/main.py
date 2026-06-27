# -*- coding: utf-8 -*-
"""Excel 盯盘工具 V2 主入口

使用方法:
    1. python main.py --generate-template   # 生成 Excel 模板（首次运行）
    2. python main.py                        # 启动盯盘

在 Excel 模板的"详细行情"和"个性定制看盘" Sheet 中填入自选股代码即可。
配置文件: config.yaml（与 main.py 同目录）
"""
import os
import sys
import time
import logging
import argparse

# 将 src 目录加入 Python 路径，使 excel_monitor 包可被导入
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_BASE_DIR, "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from excel_monitor.config_loader import AppConfig, load_config
from excel_monitor.core.data_provider import DataProvider
from excel_monitor.core.excel_manager import ExcelManager
from excel_monitor.core.config_sheet_reader import ConfigSheetReader
from excel_monitor.core.stock_pool import StockPool
from excel_monitor.sheets.market_overview import MarketOverviewSheet
from excel_monitor.sheets.detailed_quotes import DetailedQuotesSheet
from excel_monitor.sheets.news_sheet import NewsSheet
from excel_monitor.sheets.custom_watch import CustomWatchSheet
from excel_monitor.sheets.sentiment_sheet import SentimentSheet
from excel_monitor.sheets.stock_pool_sheet import StockPoolSheet
from excel_monitor.utils.template_generator import create_template


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(description="Excel 盯盘工具 V2")
    parser.add_argument(
        "--generate-template", action="store_true",
        help="生成 Excel 模板后退出（不启动盯盘）"
    )
    parser.add_argument(
        "--config", default=None,
        help="YAML 配置文件路径（默认: 同目录下的 config.yaml）"
    )
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger("main")

    # 加载配置
    yaml_path = args.config or os.path.join(_BASE_DIR, "config.yaml")
    cfg = load_config(yaml_path)
    logger.info(f"配置加载完成: {yaml_path}")

    # 1. 模板路径
    template_path = os.path.join(_BASE_DIR, cfg.excel_template)

    # 2. 如果指定 --generate-template 或模板不存在，则生成
    if args.generate_template or not os.path.exists(template_path):
        logger.info("生成 Excel 模板...")
        create_template(template_path, cfg)
        if args.generate_template:
            logger.info("模板生成完成，退出。")
            return

    # 3. 初始化组件
    excel_mgr = ExcelManager(template_path)
    data_provider = DataProvider(cfg)

    # 3.5 从 Excel "配置" Sheet 读取配置，覆盖 YAML 默认值
    config_reader = ConfigSheetReader(excel_mgr)
    cfg = config_reader.read_config(cfg.sheets["config"], cfg)
    # 配置重载后同步 enabled_backup_sources 到 DataProvider
    data_provider.enabled_sources = list(cfg.enabled_backup_sources)
    logger.info(f"刷新间隔: {cfg.refresh_interval}s, 配置重载间隔: {cfg.config_reload_interval}次")
    logger.info(f"备选数据源: {cfg.enabled_backup_sources}")

    # 4. 创建 Sheet Handlers
    handlers = [
        MarketOverviewSheet(cfg.sheets["market_overview"],
                            excel_mgr, data_provider, cfg),
        DetailedQuotesSheet(cfg.sheets["detailed_quotes"],
                            excel_mgr, data_provider, cfg),
        NewsSheet(cfg.sheets["news"],
                  excel_mgr, data_provider, cfg),
        CustomWatchSheet(cfg.sheets["custom_watch"],
                         excel_mgr, data_provider, cfg),
    ]
    # 资金情绪 Sheet（可选启用）
    if cfg.sentiment_sheet_enabled:
        handlers.append(
            SentimentSheet(cfg.sheets["sentiment"],
                           excel_mgr, data_provider, cfg)
        )
    # 股票池 Sheet（可选启用）
    stock_pool_sheet = None
    if cfg.stock_pool_sheet_enabled:
        cache_path = os.path.join(_BASE_DIR, cfg.stock_pool_cache_path)
        stock_pool = StockPool(
            cache_path=cache_path,
            cache_days=cfg.stock_pool_cache_days,
        )
        stock_pool_sheet = StockPoolSheet(
            cfg.sheets["stock_pool"], excel_mgr, data_provider, cfg, stock_pool
        )
        handlers.append(stock_pool_sheet)

    # 5. 初始化每个 Sheet
    for handler in handlers:
        try:
            handler.setup()
            handler.init()
        except Exception as e:
            logger.error(f"Sheet '{handler.name}' 初始化失败: {e}")

    # 5.5 股票池初始化成功后，为"个性定制看盘"代码列设置下拉框
    if stock_pool_sheet is not None and not stock_pool_sheet.pool.df.empty:
        try:
            custom_sheet = excel_mgr.get_sheet_by_name(cfg.sheets["custom_watch"])
            if custom_sheet is not None:
                stock_pool_sheet.setup_dropdown_for(
                    custom_sheet, col=1, start_row=2, end_row=200
                )
        except Exception as e:
            logger.warning(f"设置看盘 Sheet 下拉框失败: {e}（不影响手动输入）")

    # 6. 刷新循环
    logger.info(f"开始实时刷新，间隔 {cfg.refresh_interval} 秒...")
    try:
        while True:
            for handler in handlers:
                try:
                    handler.refresh()
                except Exception as e:
                    logger.error(f"Sheet '{handler.name}' 刷新失败: {e}")
            time.sleep(cfg.refresh_interval)
    except KeyboardInterrupt:
        logger.info("用户中断，退出...")
    finally:
        excel_mgr.close()


if __name__ == "__main__":
    main()
