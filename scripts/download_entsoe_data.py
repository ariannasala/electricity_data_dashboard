import os
from datetime import datetime

if not os.environ.get("ENTSOE_API_KEY"):
    from streamlit import secrets

    os.environ["ENTSOE_API_KEY"] = secrets["ENTSOE_API_KEY"]

from src.etl import DOWNLOADABLE_TABLES

# yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
start_date = datetime(year=2026, month=8, day=26)
countries = ["Spain", "France"]

for table in DOWNLOADABLE_TABLES:
    data = table.download(countries, start_date, end_date=start_date)

# day_ahead_prices.to_csv("tests/data/day_ahead_prices_example.csv")
# generation_long.to_csv("tests/data/generation_long_example.csv")
# load.to_csv("tests/data/load_example.csv")
