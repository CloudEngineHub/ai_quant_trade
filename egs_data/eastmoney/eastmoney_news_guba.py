# -*- coding: utf-8 -*-
# @Author   : ai_quant_trade
# @File     : eastmoney_news_guba.py
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
东方财富新闻与股吧舆情接口示例
覆盖：个股新闻、股吧帖子、股吧热度
无需安装额外库，使用 requests + pandas 即可
"""

import requests
import pandas as pd
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)
pd.set_option('display.max_colwidth', 40)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://so.eastmoney.com/'
}


def get_stock_news(keyword='601318', page=1, page_size=10):
    """
    搜索东方财富个股新闻
    :param keyword: 股票代码或关键词
    :param page: 页码
    :param page_size: 每页数量
    :return: DataFrame
    """
    url = 'https://search-api-web.eastmoney.com/chinese/json'
    params = {
        'cb': 'jQuery',
        'param': f'{{"uid":"", "keyword":"{keyword}", "type":["cmsArticleWebOld"],'
                 f'"client":"web", "clientType":"web", "clientVersion":"curr", '
                 f'"param":{{"pageNumber":{page}, "pageSize":{page_size},'
                 f'"sort":"default", "desc":"true"}}}}'
    }
    r = requests.get(url, params=params, headers=HEADERS)
    text = r.text
    # 去除 JSONP 回调包装
    if text.startswith('jQuery'):
        text = text[text.index('(') + 1: text.rindex(')')]
    import json
    data = json.loads(text)
    articles = data.get('result', {}).get('list', [])
    if not articles:
        print("未搜索到新闻")
        return pd.DataFrame()

    rows = []
    for a in articles:
        rows.append({
            '标题': a.get('title', '').replace('<em>', '').replace('</em>', ''),
            '内容': a.get('content', '')[:100],
            '发布时间': a.get('date', ''),
            '来源': a.get('mediaName', ''),
            '新闻链接': a.get('url', ''),
        })
    return pd.DataFrame(rows)


def get_guba_posts(code='601318', page=1, page_size=20):
    """
    获取东方财富股吧帖子
    :param code: 股票代码
    :param page: 页码
    :param page_size: 每页数量
    :return: DataFrame
    """
    # 股吧接口（内部API，非官方公开）
    url = 'https://guba.eastmoney.com/interface/GetData.aspx'
    headers = {
        'User-Agent': HEADERS['User-Agent'],
        'Referer': f'https://guba.eastmoney.com/list,{code}.html'
    }
    data = {
        'param': f'source=SearchResult&code={code}&type=post&sort=1&'
                 f'pagesize={page_size}&page={page}&name=zhibiao'
    }
    r = requests.post(url, data=data, headers=headers)
    try:
        result = r.json()
    except Exception:
        # 部分接口返回非JSON，尝试解析
        print(f"股吧接口返回格式异常，状态码: {r.status_code}")
        return pd.DataFrame()

    posts = result.get('Data', {}).get('data', []) if isinstance(result, dict) else []
    if not posts:
        print("未获取到股吧帖子")
        return pd.DataFrame()

    rows = []
    for p in posts[:page_size]:
        rows.append({
            '标题': p.get('post_title', ''),
            '作者': p.get('user_name', ''),
            '发布时间': pd.to_datetime(
                p.get('post_last_time', 0), unit='s'
            ).strftime('%Y-%m-%d %H:%M') if p.get('post_last_time') else '',
            '阅读量': p.get('post_click_count', 0),
            '评论数': p.get('post_comment_count', 0),
        })
    return pd.DataFrame(rows)


def get_guba_hot_list():
    """
    获取股吧热门帖子列表
    :return: DataFrame
    """
    url = 'https://guba.eastmoney.com/interface/GetData.aspx'
    headers = {
        'User-Agent': HEADERS['User-Agent'],
        'Referer': 'https://guba.eastmoney.com/'
    }
    data = {
        'param': 'source=ZhibiaoRank&ranktype=1&sort=1&pagesize=20&page=1&name=zhibiao'
    }
    r = requests.post(url, data=data, headers=headers)
    try:
        result = r.json()
    except Exception:
        print(f"股吧热门接口返回格式异常，状态码: {r.status_code}")
        return pd.DataFrame()

    posts = result.get('Data', {}).get('data', []) if isinstance(result, dict) else []
    if not posts:
        print("未获取到热门帖子")
        return pd.DataFrame()

    rows = []
    for p in posts[:20]:
        rows.append({
            '标题': p.get('post_title', ''),
            '作者': p.get('user_name', ''),
            '阅读量': p.get('post_click_count', 0),
            '评论数': p.get('post_comment_count', 0),
        })
    return pd.DataFrame(rows)


if __name__ == '__main__':
    # 1. 个股新闻
    print("=" * 60)
    print("1. 中国平安(601318) 新闻搜索")
    print("=" * 60)
    df = get_stock_news(keyword='601318', page=1, page_size=10)
    print(df)

    time.sleep(1)

    # 2. 股吧帖子
    print("\n" + "=" * 60)
    print("2. 中国平安(601318) 股吧帖子")
    print("=" * 60)
    df = get_guba_posts(code='601318', page=1, page_size=10)
    print(df)

    time.sleep(1)

    # 3. 股吧热门
    print("\n" + "=" * 60)
    print("3. 股吧热门帖子")
    print("=" * 60)
    df = get_guba_hot_list()
    print(df)
