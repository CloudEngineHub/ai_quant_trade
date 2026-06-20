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
from excel_monitor.sheets.market_overview import MarketOverviewSheet
from excel_monitor.sheets.detailed_quotes import DetailedQuotesSheet
from excel_monitor.sheets.news_sheet import NewsSheet
from excel_monitor.sheets.custom_watch import CustomWatchSheet
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
    data_provider = DataProvider()

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

    # 5. 初始化每个 Sheet
    for handler in handlers:
        try:
            handler.setup()
            handler.init()
        except Exception as e:
            logger.error(f"Sheet '{handler.name}' 初始化失败: {e}")

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
