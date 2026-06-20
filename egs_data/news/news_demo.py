# -*- coding: utf-8 -*-
# @Author   : ai_quant_trade
# @File     : news_demo.py
# @Project  : ai_quant_trade
# Copyright (c) Personal
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
财经新闻数据接口示例（基于 AKShare）
覆盖：个股新闻、财经快讯、新闻联播、微博舆情、新闻情绪指数
安装：pip install akshare --upgrade
"""

import akshare as ak
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)
pd.set_option('display.max_colwidth', 40)


def demo_stock_news():
    """1. 个股新闻（东方财富）"""
    print("=" * 60)
    print("1. 中国平安(601318) 个股新闻")
    print("=" * 60)
    df = ak.stock_news_em(symbol="601318")
    print(df.head())
    # 字段：标题、内容、发布时间、文章来源、新闻链接


def demo_global_cls():
    """2. 财联社电报快讯"""
    print("\n" + "=" * 60)
    print("2. 财联社电报快讯")
    print("=" * 60)
    df = ak.stock_info_global_cls(symbol="全部")
    print(df.head())
    # 字段：标题、内容、发布时间


def demo_global_em():
    """3. 东方财富全球财经快讯"""
    print("\n" + "=" * 60)
    print("3. 东方财富全球财经快讯")
    print("=" * 60)
    df = ak.stock_info_global_em()
    print(df.head())


def demo_global_sina():
    """4. 新浪财经全球快讯"""
    print("\n" + "=" * 60)
    print("4. 新浪财经全球快讯")
    print("=" * 60)
    df = ak.stock_info_global_sina()
    print(df.head())


def demo_news_cctv():
    """5. 新闻联播文字稿"""
    print("\n" + "=" * 60)
    print("5. 新闻联播文字稿（2024-04-24）")
    print("=" * 60)
    df = ak.news_cctv(date="20240424")
    print(df.head())
    # 字段：标题、内容


def demo_news_main_cx():
    """6. 财新网主要财经新闻"""
    print("\n" + "=" * 60)
    print("6. 财新网主要财经新闻")
    print("=" * 60)
    df = ak.stock_news_main_cx()
    print(df.head())


def demo_weibo_report():
    """7. 微博舆情报告"""
    print("\n" + "=" * 60)
    print("7. 微博舆情报告（最近12小时）")
    print("=" * 60)
    df = ak.stock_js_weibo_report(time_period="CNHOUR12")
    print(df.head())
    # 字段：股票代码、股票名称、微博舆情指数、正负面情绪占比


def demo_news_sentiment():
    """8. 新闻情绪指数"""
    print("\n" + "=" * 60)
    print("8. 新闻情绪指数")
    print("=" * 60)
    df = ak.index_news_sentiment_scope()
    print(df.tail())
    # 字段：日期、新闻情绪指数


def demo_futures_news():
    """9. 期货新闻（上海期货交易所）"""
    print("\n" + "=" * 60)
    print("9. 上海期货交易所新闻")
    print("=" * 60)
    df = ak.futures_news_shmet(symbol="全部")
    print(df.head())


if __name__ == '__main__':
    demo_stock_news()
    demo_global_cls()
    demo_global_em()
    demo_global_sina()
    demo_news_cctv()
    demo_news_main_cx()
    demo_weibo_report()
    demo_news_sentiment()
    demo_futures_news()
