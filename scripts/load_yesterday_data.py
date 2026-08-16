import os

import oracledb

from core.data_upload.download_yesterday_data import download_yesterday_data
from core.data_upload.load_data_to_oracle import load_data_to_oracle

load, day_ahead_prices, generation_long = download_yesterday_data(os.environ["COUNTRY_CODE"])

connection = oracledb.connect(
    config_dir=os.environ["WALLET_LOCATION"],
    user=os.environ["ORACLE_USER"],
    password=os.environ["ORACLE_PASSWORD"],
    dsn=os.environ["ORACLE_DSN"],
    wallet_location=os.environ["WALLET_LOCATION"],
    wallet_password=os.environ["ORACLE_WALLET_PASSWORD"],
)

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