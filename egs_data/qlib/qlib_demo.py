# -*- coding: utf-8 -*-
# @Author   : ai_quant_trade
# @File     : qlib_demo.py
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
Qlib 数据接口示例
覆盖：数据初始化、单股/多股数据获取、表达式计算
安装：pip install pyqlib
首次使用需下载数据：
    python -m qlib.run.get_data qlib_data --target_dir ~/.qlib/qlib_data/cn_data --region cn
"""

import qlib
from qlib.data import D
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)


def init_qlib():
    """1. 初始化 Qlib 中国区数据"""
    print("=" * 60)
    print("1. 初始化 Qlib（中国区数据）")
    print("=" * 60)
    qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region='cn')
    print("初始化完成")


def demo_single_stock():
    """2. 获取单只股票数据"""
    print("\n" + "=" * 60)
    print("2. 中国平安(SH601318) 日K线数据")
    print("=" * 60)
    df = D.features(
        ['SH601318'],
        ['$open', '$close', '$high', '$low', '$volume'],
        start_time='2023-01-01',
        end_time='2023-12-31'
    )
    print(df.head(10))
    # 索引为 (instrument, datetime)，列为各字段


def demo_multi_stock():
    """3. 获取多只股票数据"""
    print("\n" + "=" * 60)
    print("3. 多只股票收盘价")
    print("=" * 60)
    df = D.features(
        ['SH600000', 'SH601318', 'SZ000001'],
        ['$close'],
        start_time='2023-06-01',
        end_time='2023-06-30'
    )
    print(df.head(10))


def demo_expression():
    """4. 使用表达式计算技术指标"""
    print("\n" + "=" * 60)
    print("4. 中国平安 - 5日均线 + 涨跌幅")
    print("=" * 60)
    df = D.features(
        ['SH601318'],
        ['$close', 'Mean($close, 5)', '($close / Ref($close, 1) - 1)'],
        start_time='2023-01-01',
        end_time='2023-01-31'
    )
    print(df.head(10))
    # Mean($close, 5): 5日均线
    # Ref($close, 1): 前一日收盘价


def demo_stock_list():
    """5. 获取股票池（如沪深300成分股）"""
    print("\n" + "=" * 60)
    print("5. 沪深300成分股（前10只）")
    print("=" * 60)
    instruments = D.instruments(market='csi300')
    stock_list = D.list_instruments(instruments=instruments,
                                   start_time='2023-01-01',
                                   end_time='2023-12-31',
                                   as_list=True)
    print(stock_list[:10])


if __name__ == '__main__':
    init_qlib()
    demo_single_stock()
    demo_multi_stock()
    demo_expression()
    demo_stock_list()
