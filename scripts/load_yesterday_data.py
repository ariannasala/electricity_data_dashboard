import os
from datetime import datetime, timedelta, timezone

from src.etl.download_electricity_data import download_electricity_data
from src.etl.load_data_to_oracle import load_data_to_oracle
from src.oracle_connection import create_oracle_connection
from src.statistics.daily_statistics import (
    calculate_generation_statistics,
    calculate_price_statistics,
)

if not os.environ.get("ENTSOE_API_KEY"):
    from streamlit import secrets
    os.environ["ENTSOE_API_KEY"] = secrets["ENTSOE_API_KEY"]

countries = ["France", "Spain"]

end_date = datetime.now(timezone.utc).date()-timedelta(days=1)
start_date = end_date
load, day_ahead_prices, generation_long = download_electricity_data(countries, start_date = start_date, end_date = end_date)
print ("data downloaded")

connection = create_oracle_connection()
print ("connection created")
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
price_statistics = calculate_price_statistics(day_ahead_prices, generation_long)
load_data_to_oracle(cursor, connection, price_statistics, "prices_statistics", "prices_statistics_staging")
generation_statistics = calculate_generation_statistics(generation_long)

load_data_to_oracle(cursor, connection, generation_statistics, "generation_statistics", "generation_statistics_staging", ["timestamp", "country_code", "generation_source", "cathegory"])
connection.close()