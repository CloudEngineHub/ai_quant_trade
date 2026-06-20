# -*- coding: utf-8 -*-
# @Author   : ai_quant_trade
# @File     : fred_demo.py
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
FRED 宏观经济数据接口示例
覆盖：GDP、CPI、失业率、利率、国债收益率、美元指数
安装：pip install fredapi
注意：需免费注册获取 API Key
"""

import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)

# ============================================================
# 方式一：使用 fredapi 包
# ============================================================
def demo_fredapi():
    """使用 fredapi 包获取数据"""
    from fredapi import Fred

    # 替换为你的 API Key
    # 注册地址：https://fred.stlouisfed.org/
    FRED_API_KEY = 'YOUR_FRED_API_KEY'

    fred = Fred(api_key=FRED_API_KEY)

    # 1. GDP（季度）
    print("=" * 60)
    print("1. 美国GDP（最近5个季度）")
    print("=" * 60)
    gdp = fred.get_series('GDP')
    print(gdp.tail())

    # 2. CPI（月度）
    print("\n" + "=" * 60)
    print("2. 美国CPI消费者物价指数（最近6个月）")
    print("=" * 60)
    cpi = fred.get_series('CPIAUCSL')
    print(cpi.tail(6))

    # 3. 失业率（月度）
    print("\n" + "=" * 60)
    print("3. 美国失业率（最近6个月）")
    print("=" * 60)
    unemployment = fred.get_series('UNRATE')
    print(unemployment.tail(6))

    # 4. 联邦基金利率（月度）
    print("\n" + "=" * 60)
    print("4. 美国联邦基金利率（最近6个月）")
    print("=" * 60)
    fed_funds = fred.get_series('FEDFUNDS')
    print(fed_funds.tail(6))

    # 5. 10年期国债收益率（日频）
    print("\n" + "=" * 60)
    print("5. 美国10年期国债收益率（最近5天）")
    print("=" * 60)
    ten_year = fred.get_series('GS10')
    print(ten_year.tail())

    # 6. 美元指数
    print("\n" + "=" * 60)
    print("6. 美元指数（最近5天）")
    print("=" * 60)
    dxy = fred.get_series('DTWEXBGS')
    print(dxy.tail())


# ============================================================
# 方式二：使用 pandas_datareader（无需 fredapi 包）
# ============================================================
def demo_pandas_datareader():
    """使用 pandas_datareader 获取 FRED 数据"""
    import pandas_datareader.data as web
    import datetime

    print("=" * 60)
    print("使用 pandas_datareader 获取 FRED 数据")
    print("=" * 60)

    start = datetime.datetime(2020, 1, 1)
    end = datetime.datetime(2023, 12, 31)

    # 获取GDP
    gdp = web.DataReader('GDP', 'fred', start, end)
    print("GDP:")
    print(gdp.tail())

    # 获取多个指标
    df = web.DataReader(['GDP', 'UNRATE', 'CPIAUCSL'], 'fred', start, end)
    print("\n多指标:")
    print(df.tail())


if __name__ == '__main__':
    # 方式一需要 API Key，方式二不需要
    # 请根据需要取消注释

    # demo_fredapi()
    demo_pandas_datareader()
