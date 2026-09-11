import os

import pandas as pd

from src.etl.download_electricity_data import download_electricity_data
from src.etl.load_data_to_oracle import load_data_to_oracle
from src.oracle_connection import create_oracle_connection
from src.statistics.daily_statistics import calculate_price_statistics, calculate_generation_statistics
from src.schemas import COUNTRIES

if not os.environ.get("ENTSOE_API_KEY"):
    from streamlit import secrets

    os.environ["ENTSOE_API_KEY"] = secrets["ENTSOE_API_KEY"]

countries =list(COUNTRIES.keys())
# yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)



def load_electricity_data(global_start_date, global_end_date, countries):
    start_dates = pd.date_range(start=global_start_date, end=global_end_date, freq="D")
    connection = create_oracle_connection()
    cursor = connection.cursor()

    for i, start_date in enumerate(start_dates):
        if i != len(start_dates) - 1:
            end_date = start_dates[i + 1]
        else:
            end_date = global_end_date
        print(start_date)
        load, day_ahead_prices, generation_long = download_electricity_data(
            countries, start_date=start_date, end_date=end_date
        )
        print("data downloaded")

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
        load_data_to_oracle(
            cursor, connection, statistics, "prices_statistics", "prices_statistics_staging"
        )
        generation_statistics = calculate_generation_statistics(generation_long)

        load_data_to_oracle(cursor, connection, generation_statistics, "generation_statistics", "generation_statistics_staging", ["timestamp", "country_code", "generation_source", "cathegory"])

    connection.close()

if __name__ == "__main__":
    from datetime import datetime, timedelta
    start_date = pd.to_datetime(os.environ.get("START_DATE")) if os.environ.get("START_DATE") else None
    if not start_date:
        start_date = (datetime.now().date() - timedelta(days=3))

    end_date = pd.to_datetime(os.environ.get("END_DATE")).date() if os.environ.get("END_DATE") else None
    if not end_date:
        end_date = (datetime.now().date() - timedelta(days=1))
    load_electricity_data(start_date, end_date, countries)