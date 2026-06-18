# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd


DAILY_COLUMNS = {
    "ts_code",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "vol",
    "amount",
}


def normalize_trade_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    raw_dates = df["trade_date"].astype(str).str.strip()
    compact = raw_dates.str.match(r"^\d{8}$")
    parsed = pd.to_datetime(raw_dates, errors="coerce")
    if compact.any():
        parsed.loc[compact] = pd.to_datetime(
            raw_dates.loc[compact],
            format="%Y%m%d",
            errors="coerce",
        )
    df["trade_date"] = parsed
    return df.sort_values(["trade_date", "ts_code"]).reset_index(drop=True)


def validate_daily_frame(df: pd.DataFrame, source: str) -> None:
    missing = DAILY_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            "%s is missing required daily columns: %s"
            % (source, ", ".join(sorted(missing)))
        )


def load_local_market_data(
        csv_dir: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        benchmark: Optional[str] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load fixture or locally cached market data.

    Expected files:
      - daily.csv
      - stock_basic.csv (optional)
      - benchmark.csv (optional)
    """
    base = Path(csv_dir)
    daily_path = base / "daily.csv"
    if not daily_path.exists():
        raise FileNotFoundError("daily.csv not found in %s" % base)

    daily = pd.read_csv(daily_path)
    validate_daily_frame(daily, str(daily_path))
    daily = normalize_trade_dates(daily)

    if start_date:
        daily = daily[daily["trade_date"] >= pd.Timestamp(start_date)]
    if end_date:
        daily = daily[daily["trade_date"] <= pd.Timestamp(end_date)]

    stock_basic_path = base / "stock_basic.csv"
    if stock_basic_path.exists():
        stock_basic = pd.read_csv(stock_basic_path)
    else:
        stock_basic = pd.DataFrame({"ts_code": sorted(daily["ts_code"].unique())})

    benchmark_path = base / "benchmark.csv"
    if benchmark_path.exists():
        benchmark_df = pd.read_csv(benchmark_path)
        validate_daily_frame(benchmark_df, str(benchmark_path))
        benchmark_df = normalize_trade_dates(benchmark_df)
        if benchmark:
            benchmark_df = benchmark_df[benchmark_df["ts_code"] == benchmark]
        if start_date:
            benchmark_df = benchmark_df[
                benchmark_df["trade_date"] >= pd.Timestamp(start_date)
            ]
        if end_date:
            benchmark_df = benchmark_df[
                benchmark_df["trade_date"] <= pd.Timestamp(end_date)
            ]
    else:
        benchmark_df = pd.DataFrame()

    return daily.reset_index(drop=True), stock_basic, benchmark_df.reset_index(drop=True)


def load_tushare_market_data(
        csv_dir: str,
        start_date: str,
        end_date: str,
        benchmark: str = "000300.SH",
        token_env: str = "TUSHARE_TOKEN",
        stock_list: Optional[list] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fetch all listed A-share daily bars and cache them as CSV files."""
    token = os.environ.get(token_env)
    if not token:
        raise EnvironmentError(
            "%s is required for Tushare Pro data. "
            "Use data.source=csv for offline fixtures." % token_env
        )

    try:
        import tushare as ts
    except ImportError as exc:
        raise ImportError("tushare is required for data.source=tushare") from exc

    base = Path(csv_dir)
    base.mkdir(parents=True, exist_ok=True)
    daily_path = base / "daily.csv"
    stock_basic_path = base / "stock_basic.csv"
    benchmark_path = base / "benchmark.csv"

    if daily_path.exists() and stock_basic_path.exists():
        return load_local_market_data(csv_dir, start_date, end_date, benchmark)

    ts.set_token(token)
    pro = ts.pro_api()
    start = pd.Timestamp(start_date).strftime("%Y%m%d")
    end = pd.Timestamp(end_date).strftime("%Y%m%d")

    stock_basic, codes = select_tushare_universe(
        pro,
        stock_list=stock_list,
        stock_basic_path=stock_basic_path,
    )

    frames = []
    for code in codes:
        df = pro.daily(ts_code=code, start_date=start, end_date=end)
        if len(df):
            frames.append(df)
    if not frames:
        raise ValueError("No Tushare daily data returned for %s to %s" % (start, end))

    daily = pd.concat(frames, ignore_index=True)
    daily = daily.rename(columns={"vol": "vol", "amount": "amount"})
    daily.to_csv(daily_path, index=False)

    if benchmark:
        benchmark_df = pro.index_daily(
            ts_code=benchmark,
            start_date=start,
            end_date=end,
        )
        benchmark_df.to_csv(benchmark_path, index=False)

    return load_local_market_data(csv_dir, start_date, end_date, benchmark)


def load_market_data(
        data_config: Dict,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source = data_config.get("source", "csv")
    csv_dir = data_config.get("csv_dir", "data/momentum_rotation")
    start_date = data_config.get("start_date")
    end_date = data_config.get("end_date")
    benchmark = data_config.get("benchmark", "000300.SH")

    if source == "csv":
        return load_local_market_data(csv_dir, start_date, end_date, benchmark)
    if source == "tushare":
        return load_tushare_market_data(
            csv_dir,
            start_date,
            end_date,
            benchmark,
            stock_list=data_config.get("stock_list"),
        )
    raise ValueError("Unsupported data.source: %s" % source)


def select_tushare_universe(
        pro,
        stock_list: Optional[list],
        stock_basic_path: Path,
) -> Tuple[pd.DataFrame, list]:
    if stock_list:
        stock_basic = pd.DataFrame({"ts_code": list(stock_list)})
        stock_basic.to_csv(stock_basic_path, index=False)
        return stock_basic, list(stock_list)

    stock_basic = pro.stock_basic(
        exchange="",
        list_status="L",
        fields="ts_code,symbol,name,area,industry,market,list_date",
    )
    stock_basic.to_csv(stock_basic_path, index=False)
    codes = stock_basic["ts_code"].dropna().tolist()
    return stock_basic, codes
