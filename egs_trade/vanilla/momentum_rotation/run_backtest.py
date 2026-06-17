# -*- coding: utf-8 -*-
import argparse
import sys
from pathlib import Path
from typing import Dict

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from egs_trade.vanilla.momentum_rotation.data import load_market_data
from egs_trade.vanilla.momentum_rotation.metrics import metrics_for_period
from egs_trade.vanilla.momentum_rotation.report import (
    flatten_metrics,
    sorted_leaderboard,
    write_reports,
)
from egs_trade.vanilla.momentum_rotation.strategy import (
    MomentumRotationBacktester,
    StrategyParams,
    TradingCost,
    build_param_grid,
)


def run_from_config(config_path: str, exp_dir: str):
    with open(config_path, "r", encoding="utf-8") as fin:
        config = yaml.safe_load(fin)

    daily, stock_basic, benchmark = load_market_data(config["data"])
    base_params = _strategy_params(config.get("strategy", {}))
    cost = _trading_cost(config.get("order_cost", {}))
    params_list = build_param_grid(base_params, config.get("parameter_grid", {}))
    split = config["split"]

    rows = []
    results = []
    for param_id, params in enumerate(params_list):
        result = MomentumRotationBacktester(
            daily,
            params=params,
            cost=cost,
            stock_basic=stock_basic,
            benchmark_data=benchmark,
        ).run(start_date=split["train_start"], end_date=split["test_end"])

        train_metrics = metrics_for_period(
            result.equity_curve,
            split["train_start"],
            split["train_end"],
            benchmark,
        )
        test_metrics = metrics_for_period(
            result.equity_curve,
            split["test_start"],
            split["test_end"],
            benchmark,
        )
        row = {
            "param_id": param_id,
            "top_n": params.top_n,
            "lookback_windows": "/".join(map(str, params.lookback_windows)),
            "trailing_stop": params.trailing_stop,
            "market_filter_enabled": params.market_filter_enabled,
        }
        row.update(flatten_metrics("train", train_metrics))
        row.update(flatten_metrics("test", test_metrics))
        rows.append(row)
        results.append(result)

    leaderboard = sorted_leaderboard(rows)
    if leaderboard.empty:
        raise ValueError("No parameter result was produced")
    best_id = int(leaderboard.iloc[0]["param_id"])
    best_result = results[best_id]
    write_reports(exp_dir, leaderboard, best_result)
    return {"leaderboard": leaderboard, "best_result": best_result}


def _strategy_params(config: Dict) -> StrategyParams:
    data = StrategyParams().__dict__.copy()
    data.update(config)
    for key in ["lookback_windows", "momentum_weights", "trend_windows"]:
        if key in data:
            data[key] = tuple(data[key])
    return StrategyParams(**data)


def _trading_cost(config: Dict) -> TradingCost:
    data = TradingCost().__dict__.copy()
    data.update(config)
    return TradingCost(**data)


def get_args():
    parser = argparse.ArgumentParser(description="A-share momentum rotation")
    parser.add_argument("--config", required=True, help="config YAML path")
    parser.add_argument("--exp_dir", required=True, help="report output directory")
    return parser.parse_args()


def main():
    args = get_args()
    Path(args.exp_dir).mkdir(parents=True, exist_ok=True)
    run_from_config(args.config, args.exp_dir)


if __name__ == "__main__":
    main()
