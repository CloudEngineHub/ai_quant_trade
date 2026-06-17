# -*- coding: utf-8 -*-
from typing import Dict, Optional

import numpy as np
import pandas as pd


def _safe_float(value):
    if pd.isna(value) or np.isinf(value):
        return 0.0
    return float(value)


def calculate_metrics(
        equity_curve: pd.DataFrame,
        benchmark_df: Optional[pd.DataFrame] = None,
) -> Dict[str, float]:
    if equity_curve.empty:
        return {
            "total_return": 0.0,
            "cagr": 0.0,
            "max_drawdown": 0.0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "turnover": 0.0,
            "trade_count": 0.0,
            "benchmark_total_return": 0.0,
            "excess_total_return": 0.0,
        }

    curve = equity_curve.copy()
    curve["trade_date"] = pd.to_datetime(curve["trade_date"])
    equity = curve["equity"].astype(float)
    first = equity.iloc[0]
    last = equity.iloc[-1]
    total_return = last / first - 1 if first else 0.0
    periods = max(len(equity), 1)
    cagr = (last / first) ** (250.0 / periods) - 1 if first and last > 0 else 0.0

    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0
    returns = equity.pct_change().dropna()
    std = returns.std(ddof=0)
    sharpe = 0.0 if std == 0 or pd.isna(std) else returns.mean() / std * np.sqrt(250)
    downside = returns[returns < 0].std(ddof=0)
    sortino = (
        0.0
        if downside == 0 or pd.isna(downside)
        else returns.mean() / downside * np.sqrt(250)
    )

    benchmark_total = 0.0
    if benchmark_df is not None and not benchmark_df.empty:
        bench = benchmark_df.copy()
        bench["trade_date"] = pd.to_datetime(bench["trade_date"])
        bench = bench[
            (bench["trade_date"] >= curve["trade_date"].min())
            & (bench["trade_date"] <= curve["trade_date"].max())
        ]
        if len(bench) >= 2:
            close = bench.sort_values("trade_date")["close"].astype(float)
            benchmark_total = close.iloc[-1] / close.iloc[0] - 1

    return {
        "total_return": _safe_float(total_return),
        "cagr": _safe_float(cagr),
        "max_drawdown": _safe_float(drawdown.min()),
        "sharpe": _safe_float(sharpe),
        "sortino": _safe_float(sortino),
        "turnover": _safe_float(curve.get("turnover", pd.Series([0])).sum()),
        "trade_count": _safe_float(curve.get("trade_count", pd.Series([0])).sum()),
        "benchmark_total_return": _safe_float(benchmark_total),
        "excess_total_return": _safe_float(total_return - benchmark_total),
    }


def metrics_for_period(
        equity_curve: pd.DataFrame,
        start_date: str,
        end_date: str,
        benchmark_df: Optional[pd.DataFrame] = None,
) -> Dict[str, float]:
    curve = equity_curve.copy()
    curve["trade_date"] = pd.to_datetime(curve["trade_date"])
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    segment = curve[(curve["trade_date"] >= start) & (curve["trade_date"] <= end)]
    return calculate_metrics(segment.reset_index(drop=True), benchmark_df)
