# -*- coding: utf-8 -*-
# @Author   : ai_quant_trade
# @File     : world_bank_demo.py
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
World Bank 全球经济数据接口示例
覆盖：GDP、人口、CPI、失业率等全球指标
安装：pip install wbdata
无需 API Key
"""

import pandas as pd
import datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)


def demo_wbdata():
    """使用 wbdata 包获取数据"""
    import wbdata

    # 1. 查询国家列表
    print("=" * 60)
    print("1. 查询国家列表（前10个）")
    print("=" * 60)
    countries = wbdata.get_country()
    for c in countries[:10]:
        print(f"  {c['id']}: {c['name']}")

    # 2. 获取中国GDP
    print("\n" + "=" * 60)
    print("2. 中国GDP（2010-2023）")
    print("=" * 60)
    data = wbdata.get_data('NY.GDP.MKTP.CD', country='CHN',
                           date=('2010', '2023'))
    df = pd.DataFrame(data)
    # 提取年份和数值
    df['year'] = df['date'].apply(lambda x: x[:4])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    print(df[['year', 'value']].sort_values('year'))

    # 3. 多国多指标对比
    print("\n" + "=" * 60)
    print("3. 中美日 GDP与人口对比")
    print("=" * 60)
    indicators = {
        'NY.GDP.MKTP.CD': 'GDP(美元)',
        'SP.POP.TOTL': '人口',
        'NY.GDP.PCAP.CD': '人均GDP(美元)'
    }
    df = wbdata.get_dataframe(indicators, country=['CHN', 'USA', 'JPN'])
    print(df.head(20))


def demo_pandas_datareader():
    """使用 pandas_datareader 获取 World Bank 数据"""
    import pandas_datareader.data as web

    print("\n" + "=" * 60)
    print("使用 pandas_datareader 获取 World Bank 数据")
    print("=" * 60)

    start = datetime.datetime(2010, 1, 1)
    end = datetime.datetime(2023, 12, 31)

    # 中国GDP
    gdp_chn = web.DataReader('NY.GDP.MKTP.CD', 'wb', start, end, country='CHN')
    print("中国GDP:")
    print(gdp_chn.tail())

    # 多国GDP
    gdp_multi = web.DataReader('NY.GDP.MKTP.CD', 'wb', start, end,
                               country=['CHN', 'USA', 'JPN', 'DEU'])
    print("\n多国GDP:")
    print(gdp_multi.tail())


if __name__ == '__main__':
    demo_wbdata()
    demo_pandas_datareader()
