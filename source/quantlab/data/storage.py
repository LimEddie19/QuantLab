from pathlib import Path

import os
import tempfile
import pandas as pd

class ParquetStorage:
    def __init__(self, data_dir: str | Path = "data/raw"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, ticker: str) -> Path:
        if not ticker or not ticker.isalnum():
            raise ValueError("Ticker must be alphanumeric")

        return self.data_dir / f"{ticker.upper()}.parquet"

    def save(self, ticker: str, data: pd.DataFrame) -> None:
        if data.empty:
            raise ValueError("Cannot save an empty DataFrame")

        path = self._get_path(ticker)
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as temp_file:
                temp_path = Path(temp_file.name)

            data.to_parquet(temp_path, engine="pyarrow", index=True)

            os.replace(temp_path, path)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    def load(self, ticker: str) -> pd.DataFrame:
        path = self._get_path(ticker)

        if not path.exists():
            raise FileNotFoundError(
                f"No stored data found for {ticker}"
            )

        return pd.read_parquet(path, engine="pyarrow")

    def exists(self, ticker: str) -> bool:
        return self._get_path(ticker).exists()

    def update(self, ticker: str, data: pd.DataFrame) -> None:
        if data.empty:
            raise ValueError("Cannot update an empty DataFrame")

        if self.exists(ticker):
            existing = self.load(ticker)
            merged = pd.concat([existing, data])
        else:
            merged = data.copy()

        # Locates duplicated index and uses the latest data for idempotency
        # The ~ operator inverts the boolean array to exclude the duplicate
        merged = merged.loc[~merged.index.duplicated(keep="last")]
        merged = merged.sort_index() # sort by time

        # Saves self to temp file (Atomicity)
        # Later os.replace replaces the original with the temp if true in save function
        self.save(ticker, merged)