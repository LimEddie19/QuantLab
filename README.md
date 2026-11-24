# QuantLab

A Python-based quantitative trading research project for exploring stock-market data, developing trading strategies, and building a reproducible backtesting workflow.

> **Project status:** Early development. The market-data downloader and OHLCV validator are the first components. Strategy execution, backtesting, risk management, analytics, and a dashboard are planned, not yet implemented.

## Goals

- Download and inspect historical daily stock-market data.
- Validate market data before using it in research or simulations.
- Experiment with short-term trading strategies, including momentum and mean reversion.
- Build a backtesting engine that accounts for transaction costs and avoids look-ahead bias.
- Evaluate strategies using reproducible tests and performance metrics.

QuantLab is a learning and software engineering project, **not** a live trading system or investment recommendation service.

## Current functionality

### Historical data downloader

`src/quantlab/data/downloader.py` downloads daily OHLCV (Open, High, Low, Close, Volume) data using `yfinance` and returns a pandas DataFrame with a date index.

The current downloader requests adjusted prices (`auto_adjust=True`). Adjusted historical prices are useful for research, but they should not be treated as actual historical execution prices without further consideration.

### OHLCV validator

`src/quantlab/data/validator.py` checks that downloaded data meets basic structural requirements, including:

- Required OHLCV columns are present.
- Dates are valid, unique, and sorted.
- Prices and volume are numeric and finite.
- Prices are positive and volume is nonnegative.
- High and Low values are consistent with Open and Close.

Validation detects structural inconsistencies; it does **not** guarantee that a data provider's prices are accurate.

## Technology stack

- **Python** 3.12+
- **pandas** and **NumPy** for data processing
- **yfinance** for historical market data
- **pytest** for automated tests
- **PyArrow** for planned Parquet storage
- **Matplotlib** for planned visualizations

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/LimEddie19/QuantLab.git
cd QuantLab
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on **Windows PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on **macOS/Linux**:

```bash
source .venv/bin/activate
```

### 3. Install QuantLab

For development, including test dependencies:

```bash
python -m pip install -e ".[dev]"
```

The `-e` flag installs the project in *editable mode*, so changes to Python source files are available without reinstalling the package.

For a standard installation without development dependencies:

```bash
python -m pip install .
```

These commands require the repository's `pyproject.toml` file.

## Usage

Download and validate a stock's daily data from Python:

```python
from quantlab.data.downloader import download_stock_data
from quantlab.data.validator import validate_stock_data, get_data_summary

prices = download_stock_data("AAPL", "2024-01-01", "2025-01-01")
validate_stock_data(prices)

print(prices.head())
print(get_data_summary(prices))
```

The `start` date is inclusive and the `end` date is exclusive.

## Running tests

From the repository root, run:

```bash
python -m pytest -v
```

The validator tests cover acceptance of valid OHLCV data and rejection of selected invalid inputs.

## Project structure

```text
QuantLab/
├── src/
│   └── quantlab/
│       ├── __init__.py
│       └── data/
│           ├── __init__.py
│           ├── downloader.py
│           └── validator.py
├── tests/
│   └── test_validator.py
├── pyproject.toml
├── .gitignore
└── README.md
```

The tree above shows the initial components; additional modules will be added as development progresses.

## Roadmap

- [x] Set up the Python project and Git repository
- [x] Implement a historical OHLCV downloader
- [x] Implement an OHLCV validator
- [x] Add initial validator unit tests
- [x] Add Parquet storage and reload support
- [ ] Expand data-quality checks and automated tests
- [ ] Implement momentum and mean-reversion strategies
- [ ] Build a backtesting engine with realistic trade execution assumptions
- [ ] Add position sizing and risk management
- [ ] Calculate strategy performance and risk metrics
- [ ] Create a research dashboard
- [ ] Add out-of-sample evaluation and CI testing

The checked items reflect the components currently being developed; their behavior should be verified by running the tests locally.

## Data and research limitations

Historical market data can contain errors, gaps, and corporate-action adjustments. Backtest results are sensitive to assumptions about order timing, slippage, commissions, liquidity, and survivorship bias. QuantLab will address these issues progressively as the research pipeline matures.

## License

No license has been specified yet. Will be adding one in the future