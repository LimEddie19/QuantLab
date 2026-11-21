import pandas as pd
import yfinance as yf #Interface for retrieving data from yahoo finance


def download_stock_data(
    ticker: str,
    start: str,
    end: str
) -> pd.DataFrame:
    """
        Download daily OHLCV data for a stock.

        Parameters:
            ticker: Stock symbol, ex: NVDA (Nvidia)
            start: Inclusive start date (YYYY-MM-DD)
            end: Exclusive end date (YYYY-MM-DD)

        Returns:
            DataFrame indexed by date with OHLCV columns.
        """

    df = yf.download(
        ticker,
        start=start,
        end=end,
        interval="1d", #Split into daily sessions
        auto_adjust=True, #Built-in function to adjust for splits and re-invested dividends
        progress=False
    )

    if df.empty:
        raise ValueError(
            f"No data returned for {ticker}"
        )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    df = df[columns].copy()
    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"

    return df.sort_index()