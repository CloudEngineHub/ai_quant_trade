# -*- coding: utf-8 -*-
"""Excel 盯盘工具 V2 主入口

使用方法:
    1. python create_template.py   # 生成 Excel 模板（首次运行）
    2. python main.py               # 启动盯盘

在 Excel 模板的"详细行情"和"个性定制看盘" Sheet 中填入自选股代码即可。
"""
import os
import sys
import time
import logging

from config import AppConfig
from data_provider import DataProvider
from excel_manager import ExcelManager
from sheets.market_overview import MarketOverviewSheet
from sheets.detailed_quotes import DetailedQuotesSheet
from sheets.news_sheet import NewsSheet
from sheets.custom_watch import CustomWatchSheet


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    setup_logging()
    logger = logging.getLogger("main")
    cfg = AppConfig()

    # 1. 检查模板是否存在，不存在则生成
    template_path = os.path.join(os.getcwd(), cfg.excel_template)
    if not os.path.exists(template_path):
        logger.info("模板不存在，自动生成...")
        from create_template import create_template
        create_template(template_path)

    # 2. 初始化组件
    excel_mgr = ExcelManager(template_path)
    data_provider = DataProvider()

    # 3. 创建 Sheet Handlers
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

    # 4. 初始化每个 Sheet
    for handler in handlers:
        try:
            handler.setup()
            handler.init()
        except Exception as e:
            logger.error(f"Sheet '{handler.name}' 初始化失败: {e}")

    # 5. 刷新循环
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
