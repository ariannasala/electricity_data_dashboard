import os

import oracledb

from core.data_upload.create_tables import create_table
from core.data_upload.download_yesterday_data import download_yesterday_data

load, day_ahead_prices, generation_long = download_yesterday_data("ES")

if os.path.exists("login_information.py"):
    from scripts.login_information import (
        DB_DSN,
        DB_PASSWORD,
        DB_USER,
        WALLET_LOCATION,
        WALLET_PASSWORD,
    )

    os.environ["WALLET_LOCATION"] = WALLET_LOCATION
    os.environ["ORACLE_USER"] = DB_USER
    os.environ["ORACLE_PASSWORD"] = DB_PASSWORD
    os.environ["ORACLE_DSN"] = DB_DSN
    os.environ["ORACLE_WALLET_PASSWORD"] = WALLET_PASSWORD

connection=oracledb.connect(
    config_dir=os.environ["WALLET_LOCATION"],
    user=os.environ["ORACLE_USER"],
    password=os.environ["ORACLE_PASSWORD"],
    dsn=os.environ["ORACLE_DSN"],
    wallet_location=os.environ["WALLET_LOCATION"],
    wallet_password=os.environ["ORACLE_WALLET_PASSWORD"])

cursor = connection.cursor()


#create_table(cursor, load, "load_raw")
#create_table(cursor, load, "load_staging")
#create_table(cursor, day_ahead_prices, "day_ahead_prices_staging")
create_table(cursor, generation_long, "generation_staging")

#create_table(cursor, day_ahead_prices, "day_ahead_prices_raw")
create_table(cursor, generation_long, "generation_raw")