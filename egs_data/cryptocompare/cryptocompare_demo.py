# -*- coding: utf-8 -*-
# @Author   : ai_quant_trade
# @File     : cryptocompare_demo.py
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
CryptoCompare 电子货币行情聚合接口示例
覆盖：实时价格、市值排名、历史K线、加密货币新闻
安装：pip install requests pandas
注意：需免费注册获取 API Key
注册地址：https://min-api.cryptocompare.com/

与 CCXT 的区别：
- CCXT 直连单交易所，适合获取实时盘口和交易
- CryptoCompare 聚合多交易所，适合市值排名和历史聚合数据
"""

import requests
import pandas as pd
from datetime import datetime, timedelta

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)
pd.set_option('display.max_colwidth', 50)

BASE_URL = 'https://min-api.cryptocompare.com/data'
# 替换为你的 API Key（免费注册）
API_KEY = 'YOUR_CRYPTOCOMPARE_API_KEY'


def _get(url, params=None):
    """统一请求封装，自动附加 API Key"""
    params = params or {}
    params['api_key'] = API_KEY
    r = requests.get(f'{BASE_URL}{url}', params=params, timeout=15)
    return r


def demo_price():
    """1. 实时价格（BTC/ETH 兑 USD/CNY）"""
    print("=" * 60)
    print("1. BTC/ETH 实时价格")
    print("=" * 60)
    r = _get('/price', {
        'fsym': 'BTC',
        'tsyms': 'USD,CNY,EUR',
    })
    if r.status_code == 200:
        data = r.json()
        print(f"  BTC 兑 USD: ${data.get('USD', 0):,.2f}")
        print(f"  BTC 兑 CNY: ¥{data.get('CNY', 0):,.2f}")
        print(f"  BTC 兑 EUR: €{data.get('EUR', 0):,.2f}")
    else:
        print(f"请求失败: HTTP {r.status_code} - {r.text[:100]}")


def demo_multi_price():
    """2. 多币种价格（一次查询多个币种）"""
    print("\n" + "=" * 60)
    print("2. 多币种价格（兑USD）")
    print("=" * 60)
    r = _get('/pricemulti', {
        'fsyms': 'BTC,ETH,BNB,SOL,XRP',
        'tsyms': 'USD',
    })
    if r.status_code == 200:
        data = r.json()
        rows = []
        for coin, prices in data.items():
            rows.append({
                '币种': coin,
                '价格(USD)': prices.get('USD', 0),
            })
        print(pd.DataFrame(rows))
    else:
        print(f"请求失败: HTTP {r.status_code} - {r.text[:100]}")


def demo_top_marketcap():
    """3. 市值排名（前10）"""
    print("\n" + "=" * 60)
    print("3. 加密货币市值排名（前10）")
    print("=" * 60)
    r = _get('/top/mktcapfull', {
        'limit': 10,
        'tsym': 'USD',
    })
    if r.status_code == 200:
        data = r.json().get('Data', [])
        rows = []
        for item in data:
            info = item.get('CoinInfo', {})
            raw = item.get('RAW', {}).get('USD', {})
            rows.append({
                '币种': info.get('Name', ''),
                '全名': info.get('FullName', ''),
                '价格(USD)': raw.get('PRICE', 0),
                '市值(亿USD)': raw.get('MKTCAP', 0) / 1e8,
                '24h涨跌幅(%)': raw.get('CHANGEPCT24HOUR', 0),
            })
        df = pd.DataFrame(rows)
        print(df)
    else:
        print(f"请求失败: HTTP {r.status_code} - {r.text[:100]}")


def demo_histohour():
    """4. 历史小时K线（BTC最近24小时）"""
    print("\n" + "=" * 60)
    print("4. BTC 历史小时K线（最近24小时）")
    print("=" * 60)
    r = _get('/v2/histohour', {
        'fsym': 'BTC',
        'tsym': 'USD',
        'limit': 24,
    })
    if r.status_code == 200:
        data = r.json().get('Data', {}).get('Data', [])
        rows = []
        for d in data:
            rows.append({
                '时间': datetime.fromtimestamp(d.get('time', 0)).strftime('%Y-%m-%d %H:%M'),
                '开盘': d.get('open', 0),
                '最高': d.get('high', 0),
                '最低': d.get('low', 0),
                '收盘': d.get('close', 0),
                '成交量': d.get('volumefrom', 0),
            })
        df = pd.DataFrame(rows)
        print(df)
    else:
        print(f"请求失败: HTTP {r.status_code} - {r.text[:100]}")


def demo_news():
    """5. 加密货币新闻"""
    print("\n" + "=" * 60)
    print("5. 加密货币最新新闻")
    print("=" * 60)
    r = _get('/v2/news/', {
        'lang': 'EN',
    })
    if r.status_code == 200:
        data = r.json().get('Data', [])
        rows = []
        for n in data[:10]:
            rows.append({
                '标题': n.get('title', '')[:60],
                '来源': n.get('source_info', {}).get('name', ''),
                '发布时间': datetime.fromtimestamp(
                    n.get('published_on', 0)
                ).strftime('%Y-%m-%d %H:%M'),
                '链接': n.get('url', ''),
            })
        df = pd.DataFrame(rows)
        print(df)
    else:
        print(f"请求失败: HTTP {r.status_code} - {r.text[:100]}")


if __name__ == '__main__':
    print("CryptoCompare 电子货币行情聚合接口示例")
    print(f"API Key: {API_KEY}")
    print("请替换 YOUR_CRYPTOCOMPARE_API_KEY 后运行")
    print("注册地址: https://min-api.cryptocompare.com/")
    print()

    demo_price()
    demo_multi_price()
    demo_top_marketcap()
    demo_histohour()
    demo_news()
