# -*- coding: utf-8 -*-
# @Author   : ai_quant_trade
# @File     : efinance_demo.py
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
efinance 免费金融数据接口示例
覆盖：股票行情、实时行情、基金数据、可转债、基本信息
安装：pip install efinance
"""

import efinance as ef
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)


def demo_stock_history():
    """1. 股票历史行情"""
    print("=" * 60)
    print("1. 中国平安(601318) 历史日K线")
    print("=" * 60)
    df = ef.stock.get_quote_history('601318')
    print(df.head())
    # 字段：日期、股票代码、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅、涨跌额、换手率


def demo_stock_realtime():
    """2. 股票实时行情"""
    print("\n" + "=" * 60)
    print("2. A股实时行情（前5行）")
    print("=" * 60)
    df = ef.stock.get_realtime_quotes()
    print(df.head())


def demo_stock_info():
    """3. 个股基本信息"""
    print("\n" + "=" * 60)
    print("3. 中国平安(601318) 基本信息")
    print("=" * 60)
    df = ef.stock.get_base_info('601318')
    print(df)


def demo_fund_history():
    """4. 基金历史净值"""
    print("\n" + "=" * 60)
    print("4. 招商中证白酒基金(161725) 历史净值")
    print("=" * 60)
    df = ef.fund.get_quote_history('161725')
    print(df.head())


def demo_bond_history():
    """5. 可转债历史行情"""
    print("\n" + "=" * 60)
    print("5. 中行转债(113001) 历史行情")
    print("=" * 60)
    df = ef.stock.get_quote_history('113001', klt=101)  # klt=101 日K
    print(df.head())


def demo_belong_board():
    """6. 个股所属板块"""
    print("\n" + "=" * 60)
    print("6. 中国平安(601318) 所属板块")
    print("=" * 60)
    df = ef.stock.get_belong_board('601318')
    print(df)


if __name__ == '__main__':
    demo_stock_history()
    demo_stock_realtime()
    demo_stock_info()
    demo_fund_history()
    demo_bond_history()
    demo_belong_board()
