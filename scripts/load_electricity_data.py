import os

import pandas as pd

from src.etl import DOWNLOADABLE_TABLES
from src.etl.load_data_to_oracle import load_data_to_oracle
from src.oracle_connection import create_oracle_connection
from src.schemas import COUNTRIES
from src.daily_statistics import (
    calculate_generation_statistics,
    calculate_price_statistics,
)
from src.etl.tables import GenerationStatisticsTable, PriceStatisticsTable

if not os.environ.get("ENTSOE_API_KEY"):
    from streamlit import secrets

    os.environ["ENTSOE_API_KEY"] = secrets["ENTSOE_API_KEY"]

countries = list(COUNTRIES.keys())
# yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)


def load_electricity_data(global_start_date, global_end_date, countries, frequency="D"):
    start_dates = pd.date_range(
        start=global_start_date, end=global_end_date, freq=frequency
    )
    connection = create_oracle_connection()
    for i, start_date in enumerate(start_dates):
        if i != len(start_dates) - 1:
            end_date = start_dates[i + 1]
        else:
            end_date = global_end_date

        downloaded_data = {}
        for table in DOWNLOADABLE_TABLES:
            data = table.download(countries, start_date, end_date)
            load_data_to_oracle(connection, table, data)
            downloaded_data[table.data_name] = data

    generation_statistics = calculate_generation_statistics(
        downloaded_data["generation"]
    )
    load_data_to_oracle(connection, GenerationStatisticsTable(), generation_statistics)

    price_statistics = calculate_price_statistics(
        downloaded_data["day_ahead_prices"],
        downloaded_data["generation"],
    )
    load_data_to_oracle(connection, PriceStatisticsTable(), price_statistics)

    connection.close()


if __name__ == "__main__":
    from datetime import datetime, timedelta

    start_date = (
        pd.to_datetime(os.environ.get("START_DATE"))
        if os.environ.get("START_DATE")
        else None
    )
    if not start_date:
        start_date = datetime.now().date() - timedelta(days=3)

    end_date = (
        pd.to_datetime(os.environ.get("END_DATE")).date()
        if os.environ.get("END_DATE")
        else None
    )
    if not end_date:
        end_date = datetime.now().date() - timedelta(days=1)
    load_electricity_data(start_date, end_date, countries)
