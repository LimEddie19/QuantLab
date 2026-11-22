
import pandas as pd
import pytest

from quantlab.data.validator import validate_stock_data

@pytest.fixture
def valid_data():
    return pd.DataFrame(
        {
            "Open": [100.0, 103.0],
            "High": [105.0, 108.0],
            "Low": [98.0, 101.0],
            "Close": [103.0, 106.0],
            "Volume": [1000, 1200],
        },
        index=pd.to_datetime([
            "2025-01-02",
            "2025-01-03"
        ])
    )


def test_valid_data(valid_data):
    validate_stock_data(valid_data)


def test_negative_price(valid_data):
    valid_data.loc["2025-01-02", "Close"] = -100

    with pytest.raises(ValueError):
        validate_stock_data(valid_data)


def test_invalid_high(valid_data):
    valid_data.loc["2025-01-02", "High"] = 90

    with pytest.raises(ValueError):
        validate_stock_data(valid_data)


def test_missing_value(valid_data):
    valid_data.loc["2025-01-02", "Close"] = float("nan")

    with pytest.raises(ValueError):
        validate_stock_data(valid_data)


def test_duplicate_dates(valid_data):
    duplicate = pd.concat([
        valid_data,
        valid_data.iloc[[0]]
    ]).sort_index()

    with pytest.raises(ValueError):
        validate_stock_data(duplicate)
