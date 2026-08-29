import os
from datetime import datetime

if not os.environ.get("ENTSOE_API_KEY"):
    from streamlit import secrets
    os.environ["ENTSOE_API_KEY"] = secrets["ENTSOE_API_KEY"]

from src.etl.download_electricity_data import download_electricity_data

#yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
start_date = datetime(year = 2026, month = 6, day = 1)
country_codes = ["FR", "ES"]

load, day_ahead_prices, generation_long = download_electricity_data(country_codes, start_date = start_date, end_date = start_date)
print (load)