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


def test_update_appends_data(tmp_path, sample_data):
    storage = ParquetStorage(tmp_path)
    storage.save("NVDA", sample_data)

    new_data = sample_data.iloc[-1:].copy()
    new_data.index = pd.DatetimeIndex(
        ["2025-01-06"], name="Date"
    )

    storage.update("NVDA", new_data)

    loaded = storage.load("NVDA")

    expected = pd.concat([sample_data, new_data])

    pd.testing.assert_frame_equal(
        loaded, expected, check_freq=False
    )

def test_update_replaces_duplicates(tmp_path, sample_data):
    storage = ParquetStorage(tmp_path)
    storage.save("NVDA", sample_data)

    new_data = sample_data.iloc[-1:].copy()
    new_data["Close"] = 105.0

    storage.update("NVDA", new_data)

    loaded = storage.load("NVDA")

    assert len(loaded) == len(sample_data)
    assert loaded.index.is_unique
    assert loaded.iloc[-1]["Close"] == 105.0

def test_update_is_idempotent(tmp_path, sample_data):
    storage = ParquetStorage(tmp_path)

    storage.update("NVDA", sample_data)
    first = storage.load("NVDA")

    storage.update("NVDA", sample_data)
    second = storage.load("NVDA")

    pd.testing.assert_frame_equal(
        first, second, check_freq=False
    )

def test_update_new_ticker(tmp_path, sample_data):
    storage = ParquetStorage(tmp_path)

    storage.update("NVDA", sample_data)

    assert storage.exists("NVDA")

    pd.testing.assert_frame_equal(
        storage.load("NVDA"),
        sample_data,
        check_freq=False
    )


def test_update_sorts_dates(tmp_path, sample_data):
    storage = ParquetStorage(tmp_path)

    storage.update("NVDA", sample_data.iloc[::-1])

    loaded = storage.load("NVDA")

    assert loaded.index.is_monotonic_increasing

    pd.testing.assert_frame_equal(
        loaded, sample_data, check_freq=False
    )


def test_update_empty_dataframe(tmp_path):
    storage = ParquetStorage(tmp_path)

    with pytest.raises(ValueError):
        storage.update("NVDA", pd.DataFrame())
