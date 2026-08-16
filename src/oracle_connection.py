# database.py

import os

import oracledb


def create_oracle_connection():
    return oracledb.connect(
    config_dir=os.environ["WALLET_LOCATION"],
    user=os.environ["ORACLE_USER"],
    password=os.environ["ORACLE_PASSWORD"],
    dsn=os.environ["ORACLE_DSN"],
    wallet_location=os.environ["WALLET_LOCATION"],
    wallet_password=os.environ["ORACLE_WALLET_PASSWORD"],
)