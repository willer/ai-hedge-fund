from __future__ import annotations

import pandas as pd

from src.tools.api import get_price_data


def _get_yfinance_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame | None:
    """Fallback to yfinance for price data (free, no API key needed)."""
    try:
        import yfinance as yf
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            return None
        # Normalize column names to match our format
        data = data.rename(columns={"Close": "close", "Open": "open", "High": "high", "Low": "low", "Volume": "volume"})
        return data
    except Exception:
        return None


class BenchmarkCalculator:
    def get_return_pct(self, ticker: str, start_date: str, end_date: str) -> float | None:
        """Compute simple buy-and-hold return % for ticker from start_date to end_date.

        Return is (last_close / first_close - 1) * 100, or None if unavailable.
        Uses yfinance as fallback for tickers not available in the primary API.
        """
        df = None

        # Try primary API first
        try:
            df = get_price_data(ticker, start_date, end_date)
        except Exception:
            pass

        # Fallback to yfinance (works for SPY and other ETFs)
        if df is None or df.empty:
            df = _get_yfinance_data(ticker, start_date, end_date)

        if df is None or df.empty:
            return None

        try:
            first_close = df.iloc[0]["close"]
            last_close = df.iloc[-1]["close"]
            if first_close is None or pd.isna(first_close):
                return None
            if last_close is None or pd.isna(last_close):
                # Try last valid close
                last_valid = df["close"].dropna()
                if last_valid.empty:
                    return None
                last_close = float(last_valid.iloc[-1])
            return (float(last_close) / float(first_close) - 1.0) * 100.0
        except Exception:
            return None


