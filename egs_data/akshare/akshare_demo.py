# -*- coding: utf-8 -*-
# @Author   : ai_quant_trade
# @File     : akshare_demo.py
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
AKShare 免费金融数据接口示例
覆盖：股票行情、指数、期货、宏观经济、北向资金、财务报表
安装：pip install akshare --upgrade
"""

import akshare as ak
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)


def demo_stock_realtime():
    """1. A股实时行情（东方财富）"""
    print("=" * 60)
    print("1. A股实时行情（前5行）")
    print("=" * 60)
    df = ak.stock_zh_a_spot_em()
    print(df.head())
    # 字段：代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、振幅、最高、最低、今开、昨收、量比、换手率、市盈率-动态、市净率、总市值、流通市值


def demo_stock_hist():
    """2. 股票历史K线（前复权，日频）"""
    print("\n" + "=" * 60)
    print("2. 中国平安(601318) 历史日K线（前复权）")
    print("=" * 60)
    df = ak.stock_zh_a_hist(
        symbol="601318",
        period="daily",        # daily/weekly/monthly
        start_date="20230101",
        end_date="20231231",
        adjust="qfq"           # qfq前复权/hfq后复权/空不复权
    )
    print(df.head())
    # 字段：日期、股票代码、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅、涨跌额、换手率


def demo_index_daily():
    """3. 指数历史行情（上证指数）"""
    print("\n" + "=" * 60)
    print("3. 上证指数(sh000001) 历史行情")
    print("=" * 60)
    df = ak.stock_zh_index_daily(symbol="sh000001")
    print(df.tail())


def demo_futures():
    """4. 期货日K线数据"""
    print("\n" + "=" * 60)
    print("4. 期货日K线（PVC主力）")
    print("=" * 60)
    df = ak.futures_main_sina(symbol="V0")
    print(df.tail())
    # 字段：日期、开盘价、最高价、最低价、收盘价、成交量、持仓量、动态结算价


def demo_macro_gdp():
    """5. 宏观经济 - 中国GDP"""
    print("\n" + "=" * 60)
    print("5. 中国GDP季度数据")
    print("=" * 60)
    df = ak.macro_china_gdp()
    print(df.tail())
    # 字段：季度、国内生产总值-绝对值、国内生产总值-同比增长、第一产业-绝对值、...


def demo_north_money():
    """6. 北向资金每日净流入"""
    print("\n" + "=" * 60)
    print("6. 北向资金每日净流入")
    print("=" * 60)
    df = ak.stock_hsgt_hist_em(symbol="北向资金")
    print(df.tail())
    # 字段：日期、当日净流入、当日余额


def demo_financial_report():
    """7. 财务报表 - 资产负债表"""
    print("\n" + "=" * 60)
    print("7. 中国平安(601318) 资产负债表")
    print("=" * 60)
    df = ak.stock_financial_report_sina(stock="601318", symbol="资产负债表")
    print(df.head())
    # 返回最新报告期的资产负债表数据


def demo_fund_etf():
    """8. ETF历史行情"""
    print("\n" + "=" * 60)
    print("8. 沪深300ETF(510300) 历史行情")
    print("=" * 60)
    df = ak.fund_etf_hist_em(symbol="510300", period="daily",
                             start_date="20230101", end_date="20231231",
                             adjust="qfq")
    print(df.head())


if __name__ == '__main__':
    demo_stock_realtime()
    demo_stock_hist()
    demo_index_daily()
    demo_futures()
    demo_macro_gdp()
    demo_north_money()
    demo_financial_report()
    demo_fund_etf()
