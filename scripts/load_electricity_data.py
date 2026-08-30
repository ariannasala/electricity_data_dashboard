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

countries = ["France", "Spain"]
#yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)

global_end_date = datetime(year = 2026, month = 8, day = 28)
#global_start_date = datetime(year = global_end_date.year-1, month = 12, day = 1)
global_start_date = datetime(year = 2026, month = 8, day = 27)
start_dates = pd.date_range(start = global_start_date, end = global_end_date, freq = "D")
print (start_dates)
connection = create_oracle_connection()
cursor = connection.cursor()

for i, start_date in enumerate(start_dates):
    if i != len(start_dates)-1:
        end_date = start_dates[i+1]
    else:
        end_date = global_end_date
    print (start_date)
    load, day_ahead_prices, generation_long = download_electricity_data(countries, start_date = start_date, end_date = end_date)
    print ("data downloaded")

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