import os
from datetime import datetime, timedelta, timezone

import pandas as pd

from src.etl.download_electricity_data import download_electricity_data
from src.etl.load_data_to_oracle import load_data_to_oracle
from src.oracle_connection import create_oracle_connection
from src.statistics.daily_statistics import calculate_price_statistics

if not os.environ.get("ENTSOE_API_KEY"):
    from streamlit import secrets
    os.environ["ENTSOE_API_KEY"] = secrets["ENTSOE_API_KEY"]
    os.environ["COUNTRY_CODE"] = secrets["COUNTRY_CODE"]

yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)

load, day_ahead_prices, generation_long = download_electricity_data(os.environ["COUNTRY_CODE"], start_date = yesterday, end_date = yesterday)

connection = create_oracle_connection()
cursor = connection.cursor()

load_data_to_oracle(cursor, connection, load, "load_raw", "load_staging")

load_data_to_oracle(
    cursor,
    connection,
    day_ahead_prices,
    "day_ahead_prices_raw",
    "day_ahead_prices_staging",
)
load_data_to_oracle(
    cursor,
    connection,
    generation_long,
    "generation_raw",
    "generation_staging",
    ["timestamp", "country_code", "generation_source", "generation_type"],
)
statistics = calculate_price_statistics(day_ahead_prices, generation_long)
load_data_to_oracle(cursor, connection, statistics, "prices_statistics", "prices_statistics_staging")

connection.close()