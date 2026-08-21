import os
from datetime import datetime, timedelta, timezone

if not os.environ.get("ENTSOE_API_KEY"):
    from streamlit import secrets
    os.environ["ENTSOE_API_KEY"] = secrets["ENTSOE_API_KEY"]

from src.etl.download_electricity_data import download_electricity_data

yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)

load, day_ahead_prices, generation_long = download_electricity_data("ES", start_date = yesterday, end_date = yesterday)

load.to_csv("tests/data/load_example.csv")
day_ahead_prices.to_csv("tests/data/day_ahead_prices_example.csv")
generation_long.to_csv("tests/data/generation_long_example.csv")