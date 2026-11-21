from quantlab.data.downloader import download_stock_data

df = download_stock_data(
    "NVDA",
    "2024-01-01",
    "2025-01-01"
)

print(df.head())
print(df.info())