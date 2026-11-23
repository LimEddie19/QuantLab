import pandas as pd
import pytest

from unittest.mock import patch
from quantlab.data.storage import ParquetStorage

@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "Open": [100.0, 102.0],
            "High": [105.0, 106.0],
            "Low": [99.0, 101.0],
            "Close": [103.0, 104.0],
            "Volume": [1000000, 1200000],
        },
        index=pd.date_range(
            "2025-01-02", periods=2, freq="B", name="Date"
        ),
    )


def test_save_and_load(tmp_path, sample_data):
    storage = ParquetStorage(tmp_path)

    storage.save("NVDA", sample_data)
    loaded = storage.load("NVDA")

    pd.testing.assert_frame_equal(loaded, sample_data, check_freq=False)


def test_exists(tmp_path, sample_data):
    storage = ParquetStorage(tmp_path)

    assert not storage.exists("NVDA")

    storage.save("NVDA", sample_data)

    assert storage.exists("NVDA")


def test_missing_ticker(tmp_path):
    storage = ParquetStorage(tmp_path)

    with pytest.raises(FileNotFoundError):
        storage.load("UNKNOWN")


def test_empty_dataframe(tmp_path):
    storage = ParquetStorage(tmp_path)

    with pytest.raises(ValueError):
        storage.save("NVDA", pd.DataFrame())

def test_failed_write_preserves_original(tmp_path, sample_data):
    storage = ParquetStorage(tmp_path)

    storage.save("NVDA", sample_data)

    original = storage.load("NVDA")

    updated = sample_data.copy()
    updated["Close"] = [200.0, 201.0]

    with patch.object(
        pd.DataFrame,
        "to_parquet",
        side_effect=RuntimeError("Simulated write failure")
    ):
        with pytest.raises(RuntimeError):
            storage.save("NVDA", updated)

    recovered = storage.load("NVDA")

    pd.testing.assert_frame_equal(
        recovered,
        original,
        check_freq=False
    )

    assert list(tmp_path.iterdir()) == [
        tmp_path / "NVDA.parquet"
    ]
