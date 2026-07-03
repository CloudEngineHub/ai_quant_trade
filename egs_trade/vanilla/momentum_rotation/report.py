# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Iterable

import pandas as pd


def write_reports(exp_dir: str, leaderboard: pd.DataFrame, best_result) -> None:
    out = Path(exp_dir)
    out.mkdir(parents=True, exist_ok=True)

    leaderboard.to_csv(out / "leaderboard.csv", index=False)
    best_result.equity_curve.to_csv(out / "equity_curve.csv", index=False)
    best_result.trades.to_csv(out / "trades.csv", index=False)
    pd.DataFrame([best_result.metrics]).to_csv(out / "metrics.csv", index=False)
    _plot_equity_curve(best_result.equity_curve, out / "equity_curve.png")


def _plot_equity_curve(equity_curve: pd.DataFrame, save_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4))
    curve = equity_curve.copy()
    curve["trade_date"] = pd.to_datetime(curve["trade_date"])
    ax.plot(curve["trade_date"], curve["equity"], label="strategy")
    ax.set_xlabel("date")
    ax.set_ylabel("equity")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def flatten_metrics(prefix: str, metrics: dict) -> dict:
    return {prefix + "_" + key: value for key, value in metrics.items()}


def sorted_leaderboard(rows: Iterable[dict]) -> pd.DataFrame:
    df = pd.DataFrame(list(rows))
    if df.empty:
        return df
    return df.sort_values(
        ["test_cagr", "test_total_return"],
        ascending=[False, False],
    ).reset_index(drop=True)
