# -*- coding: utf-8 -*-
from dataclasses import dataclass
from itertools import product
from typing import Dict, Iterable, List, Optional, Sequence

import pandas as pd


@dataclass(frozen=True)
class TradingCost:
    open_commission: float = 0.0
    close_commission: float = 0.0
    close_tax: float = 0.0
    min_commission: float = 0.0
    slippage_bps: float = 0.0


@dataclass(frozen=True)
class StrategyParams:
    initial_cash: float = 100000.0
    top_n: int = 10
    lookback_windows: Sequence[int] = (20, 60, 120)
    momentum_weights: Sequence[float] = (0.5, 0.3, 0.2)
    trend_windows: Sequence[int] = (20, 60)
    volatility_window: int = 20
    volatility_penalty: float = 0.5
    min_avg_amount: float = 50000000.0
    liquidity_window: int = 20
    trailing_stop: float = 0.15
    market_filter_enabled: bool = True
    market_ma_window: int = 60
    min_list_days: int = 180
    exclude_st: bool = True
    lot_size: int = 100


@dataclass
class BacktestResult:
    equity_curve: pd.DataFrame
    trades: pd.DataFrame
    metrics: Dict[str, float]
    params: StrategyParams


def build_param_grid(base_params: StrategyParams, grid: Dict) -> List[StrategyParams]:
    if not grid:
        return [base_params]

    keys = sorted(grid.keys())
    values = [grid[key] for key in keys]
    params = []
    for combo in product(*values):
        data = base_params.__dict__.copy()
        for key, value in zip(keys, combo):
            if key in {"lookback_windows", "momentum_weights", "trend_windows"}:
                value = tuple(value)
            data[key] = value
        params.append(StrategyParams(**data))
    return params


class MomentumRotationBacktester:
    def __init__(
            self,
            daily_data: pd.DataFrame,
            params: StrategyParams,
            cost: TradingCost,
            stock_basic: Optional[pd.DataFrame] = None,
            benchmark_data: Optional[pd.DataFrame] = None,
    ):
        self.params = params
        self.cost = cost
        self.stock_basic = stock_basic if stock_basic is not None else pd.DataFrame()
        self.benchmark_data = (
            benchmark_data if benchmark_data is not None else pd.DataFrame()
        )
        self.daily = self._prepare_daily(daily_data)
        self.close = self._pivot("close")
        self.open = self._pivot("open")
        self.amount = self._pivot("amount")
        self.trade_dates = sorted(self.daily["trade_date"].unique())

    def run(
            self,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
    ) -> BacktestResult:
        cash = float(self.params.initial_cash)
        positions: Dict[str, Dict[str, float]] = {}
        trade_rows = []
        equity_rows = []

        run_dates = self._run_dates(start_date, end_date)
        previous_date = None
        for idx, trade_date in enumerate(run_dates):
            decision_date = self._previous_available_date(trade_date)
            day_turnover = 0.0
            day_trade_count = 0

            if decision_date is not None:
                stop_orders = self._trailing_stop_orders(positions, decision_date)
                for code in stop_orders:
                    sold = self._sell_position(
                        code,
                        trade_date,
                        cash,
                        positions,
                        reason="trailing_stop",
                    )
                    cash = sold["cash"]
                    if sold["trade"] is not None:
                        trade_rows.append(sold["trade"])
                        day_turnover += sold["trade"]["value"]
                        day_trade_count += 1

            if decision_date is not None and self._should_rebalance(
                    trade_date, previous_date, idx
            ):
                targets = self._select_targets(decision_date)
                rebalanced = self._rebalance(
                    trade_date,
                    targets,
                    cash,
                    positions,
                )
                cash = rebalanced["cash"]
                trade_rows.extend(rebalanced["trades"])
                day_turnover += rebalanced["turnover"]
                day_trade_count += len(rebalanced["trades"])

            self._update_high_water(positions, trade_date)
            equity = self._mark_to_market(cash, positions, trade_date)
            exposure = self._gross_exposure(equity, positions, trade_date)
            equity_rows.append({
                "trade_date": pd.Timestamp(trade_date).strftime("%Y-%m-%d"),
                "equity": equity,
                "cash": cash,
                "gross_exposure": exposure,
                "position_count": len(positions),
                "turnover": day_turnover,
                "trade_count": day_trade_count,
            })
            previous_date = trade_date

        equity_curve = pd.DataFrame(equity_rows)
        trades = pd.DataFrame(trade_rows)
        from egs_trade.vanilla.momentum_rotation.metrics import calculate_metrics

        metrics = calculate_metrics(equity_curve, self.benchmark_data)
        return BacktestResult(equity_curve, trades, metrics, self.params)

    def _prepare_daily(self, daily_data: pd.DataFrame) -> pd.DataFrame:
        df = daily_data.copy()
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        for col in ["open", "high", "low", "close", "vol", "amount"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["ts_code", "trade_date", "open", "close"])
        return df.sort_values(["trade_date", "ts_code"]).reset_index(drop=True)

    def _pivot(self, column: str) -> pd.DataFrame:
        return self.daily.pivot(index="trade_date", columns="ts_code", values=column)

    def _run_dates(self, start_date: Optional[str], end_date: Optional[str]):
        dates = self.trade_dates
        if start_date:
            dates = [d for d in dates if d >= pd.Timestamp(start_date)]
        if end_date:
            dates = [d for d in dates if d <= pd.Timestamp(end_date)]
        return dates

    def _previous_available_date(self, trade_date):
        previous = [d for d in self.trade_dates if d < trade_date]
        return previous[-1] if previous else None

    def _should_rebalance(self, trade_date, previous_run_date, run_index):
        if run_index == 0:
            return True
        if previous_run_date is None:
            return False
        return pd.Timestamp(trade_date).month != pd.Timestamp(previous_run_date).month

    def _select_targets(self, decision_date) -> List[str]:
        if self.params.market_filter_enabled and not self._market_allows_risk(
                decision_date
        ):
            return []

        score_rows = []
        for code in self.close.columns:
            score = self._score_code(code, decision_date)
            if score is not None:
                score_rows.append((code, score))
        score_rows.sort(key=lambda row: row[1], reverse=True)
        return [code for code, _ in score_rows[:self.params.top_n]]

    def _score_code(self, code: str, decision_date):
        if not self._passes_stock_filters(code, decision_date):
            return None
        if code not in self.close.columns:
            return None
        series = self.close[code].loc[:decision_date].dropna()
        if series.empty:
            return None
        max_window = max(list(self.params.lookback_windows) + [1])
        if len(series) <= max_window:
            return None

        current = series.iloc[-1]
        score = 0.0
        for window, weight in zip(
                self.params.lookback_windows, self.params.momentum_weights
        ):
            base = series.iloc[-window - 1]
            if base <= 0:
                return None
            score += weight * (current / base - 1.0)

        if self.params.trend_windows:
            for window in self.params.trend_windows:
                if len(series) < window:
                    return None
                if current < series.tail(window).mean():
                    return None

        amount = self.amount[code].loc[:decision_date].dropna()
        if len(amount) < self.params.liquidity_window:
            return None
        if amount.tail(self.params.liquidity_window).mean() < self.params.min_avg_amount:
            return None

        returns = series.pct_change().dropna()
        if len(returns) >= self.params.volatility_window:
            vol = returns.tail(self.params.volatility_window).std(ddof=0)
            score -= self.params.volatility_penalty * vol
        return float(score)

    def _passes_stock_filters(self, code: str, decision_date) -> bool:
        if self.stock_basic.empty:
            return True
        rows = self.stock_basic[self.stock_basic["ts_code"] == code]
        if rows.empty:
            return True
        row = rows.iloc[0]
        if self.params.exclude_st:
            name = str(row.get("name", ""))
            is_st = str(row.get("is_st", "0")).lower() in {"1", "true", "yes"}
            if is_st or "ST" in name.upper():
                return False
        list_date = row.get("list_date")
        if pd.notna(list_date) and self.params.min_list_days > 0:
            listed = pd.to_datetime(str(int(list_date)), format="%Y%m%d")
            age = (pd.Timestamp(decision_date) - listed).days
            if age < self.params.min_list_days:
                return False
        return True

    def _market_allows_risk(self, decision_date) -> bool:
        if self.benchmark_data.empty:
            return True
        bench = self.benchmark_data.copy()
        bench["trade_date"] = pd.to_datetime(bench["trade_date"])
        bench = bench[bench["trade_date"] <= decision_date].sort_values("trade_date")
        if len(bench) < self.params.market_ma_window:
            return True
        close = bench["close"].astype(float)
        return close.iloc[-1] >= close.tail(self.params.market_ma_window).mean()

    def _trailing_stop_orders(self, positions, decision_date) -> List[str]:
        codes = []
        for code, pos in positions.items():
            if code not in self.close.columns or decision_date not in self.close.index:
                continue
            close = self.close.at[decision_date, code]
            if pd.isna(close):
                continue
            if close <= pos["high_water"] * (1.0 - self.params.trailing_stop):
                codes.append(code)
        return codes

    def _rebalance(self, trade_date, targets: Iterable[str], cash, positions):
        targets = list(targets)
        trades = []
        turnover = 0.0

        for code in list(positions.keys()):
            if code not in targets:
                sold = self._sell_position(
                    code, trade_date, cash, positions, reason="rebalance"
                )
                cash = sold["cash"]
                if sold["trade"] is not None:
                    trades.append(sold["trade"])
                    turnover += sold["trade"]["value"]

        if not targets:
            return {"cash": cash, "trades": trades, "turnover": turnover}

        equity = self._mark_to_market(cash, positions, trade_date)
        target_value = equity / len(targets)

        for code in targets:
            current_value = self._position_value(code, positions, trade_date)
            diff = target_value - current_value
            if diff <= 0:
                continue
            bought = self._buy_value(
                code,
                trade_date,
                min(diff, cash),
                cash,
                positions,
                reason="rebalance",
            )
            cash = bought["cash"]
            if bought["trade"] is not None:
                trades.append(bought["trade"])
                turnover += bought["trade"]["value"]

        return {"cash": cash, "trades": trades, "turnover": turnover}

    def _buy_value(self, code, trade_date, target_cash, cash, positions, reason):
        price = self._execution_price(code, trade_date, "buy")
        if price is None or target_cash <= 0:
            return {"cash": cash, "trade": None}
        shares = self._shares_for_cash(target_cash, price)
        while shares > 0:
            value = shares * price
            fee = self._fee(value, "buy")
            if value + fee <= cash + 1.0e-8:
                break
            shares -= self.params.lot_size
        if shares <= 0:
            return {"cash": cash, "trade": None}

        value = shares * price
        fee = self._fee(value, "buy")
        cash -= value + fee
        if code in positions:
            old = positions[code]
            old_value = old["shares"] * old["entry_price"]
            total_shares = old["shares"] + shares
            avg_price = (old_value + value) / total_shares
            old["shares"] = total_shares
            old["entry_price"] = avg_price
        else:
            positions[code] = {
                "shares": shares,
                "entry_price": price,
                "high_water": price,
            }
        return {
            "cash": cash,
            "trade": self._trade_row(
                trade_date, code, "buy", shares, price, value, fee, reason, cash
            ),
        }

    def _sell_position(self, code, trade_date, cash, positions, reason):
        if code not in positions:
            return {"cash": cash, "trade": None}
        price = self._execution_price(code, trade_date, "sell")
        if price is None:
            return {"cash": cash, "trade": None}
        shares = positions[code]["shares"]
        value = shares * price
        fee = self._fee(value, "sell")
        cash += value - fee
        positions.pop(code)
        return {
            "cash": cash,
            "trade": self._trade_row(
                trade_date, code, "sell", shares, price, value, fee, reason, cash
            ),
        }

    def _shares_for_cash(self, cash, price):
        shares = int(cash / price)
        lot = max(int(self.params.lot_size), 1)
        return int(shares / lot) * lot

    def _execution_price(self, code, trade_date, side):
        if code not in self.open.columns or trade_date not in self.open.index:
            return None
        price = self.open.at[trade_date, code]
        if pd.isna(price):
            return None
        slip = self.cost.slippage_bps / 10000.0
        if side == "buy":
            return float(price) * (1.0 + slip)
        return float(price) * (1.0 - slip)

    def _fee(self, value, side):
        if side == "buy":
            rate = self.cost.open_commission
            tax = 0.0
        else:
            rate = self.cost.close_commission
            tax = self.cost.close_tax * value
        commission = rate * value
        if value > 0 and commission < self.cost.min_commission:
            commission = self.cost.min_commission
        return commission + tax

    def _trade_row(
            self, trade_date, code, side, shares, price, value, fee, reason, cash
    ):
        return {
            "trade_date": pd.Timestamp(trade_date).strftime("%Y-%m-%d"),
            "ts_code": code,
            "side": side,
            "shares": shares,
            "price": price,
            "value": value,
            "fee": fee,
            "reason": reason,
            "cash_after": cash,
        }

    def _update_high_water(self, positions, trade_date):
        for code, pos in positions.items():
            if code not in self.close.columns or trade_date not in self.close.index:
                continue
            close = self.close.at[trade_date, code]
            if not pd.isna(close):
                pos["high_water"] = max(pos["high_water"], float(close))

    def _mark_to_market(self, cash, positions, trade_date):
        return cash + sum(
            self._position_value(code, positions, trade_date)
            for code in positions
        )

    def _position_value(self, code, positions, trade_date):
        if code not in positions:
            return 0.0
        if code in self.close.columns and trade_date in self.close.index:
            price = self.close.at[trade_date, code]
            if not pd.isna(price):
                return float(price) * positions[code]["shares"]
        return positions[code]["entry_price"] * positions[code]["shares"]

    def _gross_exposure(self, equity, positions, trade_date):
        if equity <= 0:
            return 0.0
        invested = sum(
            self._position_value(code, positions, trade_date)
            for code in positions
        )
        return invested / equity
