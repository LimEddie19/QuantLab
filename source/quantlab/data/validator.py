import numpy as np
import pandas as pd
from pandas.core.interchange import column

REQUIRED_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume"
]

def validate_stock_data(df: pd.DataFrame) -> None:
    #Section 1: validates aggregate data and formatting
    if df.empty:
        raise ValueError("Stock data is empty")

    #See what is missing from REQUIRED
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(f"Index is not a datetime index")

    if df.index.has_duplicates:
        raise ValueError(f"Index has duplicate dates")

    #Make sure the rows are ordered correctly to avoid inconsistent move operations
    if not df.index.is_monotonic_increasing:
        raise ValueError(f"Dates are not sorted")

    #Section 2: Validate numerical values
    prices = df[["Open", "High", "Low", "Close"]]
    volume = df[["Volume"]]

    if any(
        not pd.api.types.is_numeric_dtype(df[column])
        or pd.api.types.is_bool_dtype(df[column])
        for column in REQUIRED_COLUMNS
    ):
        raise ValueError(f"OHLCV columns must be numeric")

    #Reject missing or infinite values
    if not np.isfinite(df[REQUIRED_COLUMNS].to_numpy()).all():
        raise ValueError(f"Missing or Infinite value detected")

    #Prices have to be positive
    if (prices <=0).any().any():
        raise ValueError(f"Prices cannot be negative")

    #Volume has to be positive
    if (volume <=0).any().any():
        raise ValueError(f"Volume cannot be negative")

    #Section 3: Validate data logic in relation to other columns
    invalid_high = (
        df["High"] < df[["Open", "Low", "Close"]].max(axis=1)
    )

    invalid_low = (
        df["Low"] > df[["Open", "High", "Close"]].min(axis=1)
    )

    if invalid_high.any():
        raise ValueError(f"Invalid High prices detected")

    if invalid_low.any():
        raise ValueError(f"Invalid Low prices detected")

def get_data_summary(df: pd.DataFrame) -> dict:
    """Summarize an already validated dataset."""

    validate_stock_data(df)

    return {
        "rows": len(df),
        "start_date": str(df.index.min().date()),
        "end_date": str(df.index.max().date()),
        "average_volume": float(df["Volume"].mean()),
        "min_close": float(df["Close"].min()),
        "max_close": float(df["Close"].max()),
    }
