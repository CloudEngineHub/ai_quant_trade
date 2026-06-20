# 0. 简介

本样例中提供各类数据处理流程。

推荐源汇总：

![](.README_images/数据源汇总.png)

# 1. 推荐使用数据源

1. 收费数据：
    - Wind数据(业内权威，机构首选数据)

2. 部分收费数据
    - Tushare（若免费使用，接口调用受限）
    - 聚宽

3. 免费数据
    - Baostock
    - qstock (主要基于东方财富和同花顺的免费接口)
    - AKShare (目前最全的免费金融数据接口库)
    - efinance (基于东方财富的免费数据获取库)
    - Qlib (微软开源AI量化框架，内置数据下载)
    - CCXT (加密货币交易所统一接口库)
    - CryptoCompare (加密货币行情聚合，需免费API Key)
    - FRED (美联储宏观经济数据)
    - World Bank API (全球经济数据)
    - 巨潮资讯网 (官方信息披露平台)
    - GDELT Project (全球新闻事件+情绪数据)
    - Finnhub (国际财经新闻+情绪分析)
    - NewsAPI.org (国际新闻聚合API)
    - 雪球网 (投资者社区舆情数据)

# 2. 开源股票数据获取途径
## 2.1 开源免费python库
&emsp;&emsp;免费数据足够研究使用，实盘使用，质量可能略微欠佳。
常见开源数据python库如下：

- qlib [https://github.com/microsoft/qlib](https://github.com/microsoft/qlib)    
  * （*****）推荐使用
  * 微软开源AI量化框架，通过雅虎财经获取数据，可获取中国和美国区数据。该数据
  足够进行研究，但质量欠佳，实盘建议更换质量更高的数据。
  * [示例代码](qlib/qlib_demo.py)

- [证券宝](www.baostock.com) 
  * （*****）推荐使用
  * 免注册证券数据 (数据很丰富，qlib基于此获取数据)

- akshare [https://github.com/akfamily/akshare](https://github.com/akfamily/akshare)
  * （*****）推荐使用
  * 非常完善的数据获取库，主要基于爬虫获取，覆盖股票/期货/期权/基金/外汇/债券/宏观经济等
  * [示例代码](akshare/akshare_demo.py)

- efinance [https://github.com/Micro-sheep/efinance](https://github.com/Micro-sheep/efinance)
  * （*****）推荐使用
  * 非常完善的数据获取库，主要基于爬虫获取
  * 缺点: 没有大盘指数的接口
  * [示例代码](efinance/efinance_demo.py)

- yfinance
  * （***）推荐使用 (貌似只能获取国外股票行情数据)
  * 前身是pandas_datareader，后来雅虎关闭api后，通过一些非官方方法获取数据
  * 优点是数据免费、可以获取分钟级数据

- pandas_datareader
  - 库以失效，无法获取数据    

## 2.2 财经网API获取数据
- 新浪财经API
  * （***）推荐使用
  * 不确定调用量限制，另外，获取的数据是json格式，需要自行整理数据
  * 查询不了历史数据，只能获取实时数据
  * [示例代码](web_api/demo_sina_data.ipynb)

- 东方财富API
  * （****）推荐使用
  * 无需注册，返回JSON，数据丰富（K线/实时/资金流）
  * 是akshare、efinance等库的底层数据源
  * [示例代码](eastmoney/eastmoney_api.py)

- 腾讯财经API
  * （***）推荐使用
  * 数据较丰富，支持实时行情和历史K线
  * [示例代码](tencent/tencent_api.py)

- 网易财经API
  * （***）推荐使用
  * 支持CSV下载，历史数据较长
  * [示例代码](netease/netease_api.py)

- 雅虎财经API(已关闭，但通过一些python库仍能获取相关数据)

## 2.3 加密货币数据
- CCXT [https://github.com/ccxt/ccxt](https://github.com/ccxt/ccxt)
  * （*****）推荐使用
  * 支持100+加密货币交易所的统一接口
  * 公开行情数据无需API Key
  * [示例代码](ccxt/ccxt_demo.py)

- CryptoCompare
  * （****）推荐使用
  * 加密货币行情聚合，多交易所加权价格、市值排名、历史数据
  * 与CCXT互补：CCXT直连单交易所，CryptoCompare聚合全市场
  * 免费层需注册 API Key
  * [示例代码](cryptocompare/cryptocompare_demo.py)

## 2.4 期货数据
- AKShare 期货接口（新浪财经）
  * （*****）推荐使用
  * 覆盖主力连续日K线、单合约历史K线、全市场主力合约列表
  * 无需 API Key
  * [示例代码](futures/futures_demo.py)

## 2.5 基金数据
- AKShare + efinance 基金接口
  * （*****）推荐使用
  * 覆盖开放式基金净值、基金业绩排行、基金持仓、ETF行情
  * 无需 API Key
  * [示例代码](fund/fund_demo.py)

## 2.6 海外宏观数据
- FRED (Federal Reserve Economic Data)
  * （*****）推荐使用
  * 美联储免费宏观经济数据库，数据权威
  * 需免费注册获取API Key
  * [示例代码](fred/fred_demo.py)

- World Bank API
  * （****）推荐使用
  * 世界银行免费全球经济数据，覆盖200+国家
  * 无需API Key
  * [示例代码](world_bank/world_bank_demo.py)

## 2.7 官方披露数据
- 巨潮资讯网 (CNINFO)
  * （****）推荐使用
  * 证监会指定法定信息披露网站
  * 提供上市公司公告、年报、季报等
  * [示例代码](cninfo/cninfo_demo.py)

## 2.8 财经新闻数据
- AKShare 新闻接口
  * （*****）推荐使用
  * 覆盖个股新闻、财经快讯、新闻联播、微博舆情、新闻情绪指数
  * 无需 API Key，接口最全
  * [示例代码](news/news_demo.py)

- 东方财富新闻+股吧
  * （****）推荐使用
  * 个股新闻搜索、股吧帖子、股吧热度
  * 无需 API Key
  * [示例代码](eastmoney/eastmoney_news_guba.py)

- GDELT Project
  * （*****）推荐使用
  * 全球新闻事件数据库，1979年至今，每15分钟更新
  * 内置CAMEO事件编码和Tone情绪分数
  * 完全免费，无需 API Key
  * [示例代码](gdelt/gdelt_demo.py)

- Finnhub
  * （****）推荐使用
  * 国际财经新闻、公司新闻、新闻情绪分析
  * 免费层60请求/分钟，需注册 API Key
  * [示例代码](finnhub/finnhub_demo.py)

- NewsAPI.org
  * （****）推荐使用
  * 覆盖150,000+全球新闻源，55个国家，14种语言
  * 免费层100请求/天，需注册 API Key
  * [示例代码](news_api/newsapi_demo.py)

## 2.9 舆情数据
- 雪球网
  * （****）推荐使用
  * 国内领先投资者社区，帖子内容、阅读量、评论数
  * 需登录获取 Cookie（xq_a_token）
  * [示例代码](xueqiu/xueqiu_demo.py)

- 东方财富股吧
  * （****）推荐使用
  * A股最大散户社区，舆情反向指标价值高
  * 无需 API Key
  * [示例代码](eastmoney/eastmoney_news_guba.py)

## 2.10 部分免费python库
&emsp;&emsp;该部分数据质量相对较好，但不完全免费，存在部分限制。

- 国内量化在线平台
  * （*****）推荐使用
  * 如优矿、果仁、米筐、聚宽等
  * 聚宽提供3个月免费本地数据服务
  * 在平台上可以方便的获取行情数据，通过dataframe可以下载少量数据，
    进行本地实验，但数据量大了，下载较为麻烦，且不确定是否有限制
  
- Tushare [**https://tushare.pro/**](https://tushare.pro/)  
  * （*****）推荐使用
  * 质量高，使用人数多。但存在很多限制，需要收费才能获取更多的数据。
  
# 3. 收费股票数据获取途径   
收费数据质量更高，更可靠。
- Wind: 几乎所有金融机构的首选，如果用于个人，费用可能有些小贵哦
- “三大矿”在线平台：如聚宽、米筐和优矿等。对于聚宽，费用对于个人还可以，
  其余2个平台，我还未进行调研。但聚宽上的行业分类，相比同花顺，感觉很久
  没有更新了，比较老，不知道VIP的接口获取的数据是否是不同的

# 4. 数据源列表
## 4.1 免费
* Baostock - 免注册证券数据
* qstock - 基于东方财富和同花顺的免费接口
* AKShare - 最全免费金融数据接口库（含新闻/舆情/期货/基金接口）
* efinance - 基于东方财富的免费数据获取库
* Qlib - 微软开源AI量化框架
* CCXT - 加密货币交易所统一接口库
* FRED - 美联储宏观经济数据
* World Bank API - 全球经济数据
* 巨潮资讯网 - 官方信息披露平台
* GDELT Project - 全球新闻事件+情绪数据（1979年至今）
* 新浪、雅虎、东方财富网、腾讯、网易 - 财经网API
* 通达信 - 免费
* 历史数据 - 文档 | BigQuant - 免费

## 4.2 免费（需注册 API Key）
* CryptoCompare - 加密货币行情聚合（市值排名/历史数据）
* Finnhub - 国际财经新闻+情绪分析（60请求/分钟）
* NewsAPI.org - 国际新闻聚合API（100请求/天）
* 雪球网 - 投资者社区舆情数据（需Cookie）

## 4.3 部分免费
* TuShare - 中文财经数据接口包（免费额度有限）
* 聚宽 - 提供3个月免费本地数据服务
* 优矿、果仁、米筐 - 在线平台部分免费

## 4.4 收费
* Quandl - 国际金融和经济数据（部分免费）
* Wind资讯-经济数据库 - 收费
* 东方财富 Choice金融数据研究终端 - 收费
* iFinD 同花顺金融数据终端 - 收费
* 朝阳永续 Go-Goal数据终端 - 收费
* 天软数据 - 收费
* 国泰安数据服务中心 - 收费
* 锐思数据 - 收费
* 恒生API - 收费
* Bloomberg API - 收费
* 数库金融数据和深度分析API服务 - 收费
* Historical Data Sources - 一个数据源索引
* 预测者网 - 收费
* 通联数据商城 - 收费
* 聚合数据、数粮 、数据宝 - 收费