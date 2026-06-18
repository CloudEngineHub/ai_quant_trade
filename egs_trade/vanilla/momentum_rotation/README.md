# A股全市场强势股轮动回测策略

这是一个研究回测示例，不是投资建议，不承诺任何年化收益。
策略只做多、不融资、不做空、不接模拟盘或实盘。

## 思路

- 每月第一个可交易日换仓。
- 使用上一交易日的可见数据打分，下一交易日按开盘价模拟成交。
- 动量分数默认使用 20/60/120 日收益，叠加波动惩罚、成交额过滤、
  均线趋势过滤。
- 参数搜索默认覆盖 `top_n=[5,10,20]`、移动止损阈值和大盘过滤开关。
- 总仓位不超过 100%，移动止损卖出后资金留作现金，直到下次换仓。

## 数据

Tushare Pro 模式读取环境变量 `TUSHARE_TOKEN`：

```shell
set TUSHARE_TOKEN=your-token
python run_backtest.py --config conf/momentum_rotation.yaml --exp_dir exp/momentum_rotation
```

如需避开 `stock_basic` 的低频率限制，可在配置的 `data` 下添加
`stock_list: [000001.SZ, 600000.SH]`，直接验证指定股票的真实行情链路。

离线验证可把配置里的 `data.source` 改为 `csv`，并提供：

- `daily.csv`
- `stock_basic.csv`
- `benchmark.csv`

`daily.csv` 至少包含：
`ts_code,trade_date,open,high,low,close,vol,amount`。

## 输出

`exp_dir` 下会生成：

- `leaderboard.csv`：按样本外 `test_cagr` 降序排列的参数榜单。
- `equity_curve.csv`：样本外榜首参数的资金曲线。
- `trades.csv`：样本外榜首参数的交易明细。
- `metrics.csv`：榜首参数的总体指标。
- `equity_curve.png`：资金曲线图。

## 风险说明

强势股轮动偏收益优先，容易在趋势反转或流动性恶化时出现较大回撤。
回测结果受数据质量、复权方式、停牌/涨跌停处理、交易成本和样本切分影响。
实盘前必须单独验证数据、交易规则、滑点、容量和风控。
