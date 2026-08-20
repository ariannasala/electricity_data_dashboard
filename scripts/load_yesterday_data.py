import os
from datetime import datetime, timedelta, timezone

from src.etl.download_electricity_data import download_electricity_data
from src.etl.load_data_to_oracle import load_data_to_oracle
from src.oracle_connection import create_oracle_connection

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

connection.close()