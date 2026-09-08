from src.statistics.daily_statistics import calculate_price_statistics, calculate_generation_statistics
from src.oracle_connection import create_oracle_connection
from src.etl.read_data_from_oracle import read_data_from_oracle
from src.etl.load_data_to_oracle import load_data_to_oracle

import os
if not os.environ.get("ENTSOE_API_KEY"):
    from streamlit import secrets
    os.environ["ORACLE_PASSWORD"] = secrets["ORACLE_PASSWORD"]
    os.environ["ORACLE_USER"] = secrets["ORACLE_USER"]
    os.environ["ORACLE_WALLET_PASSWORD"] = secrets["ORACLE_WALLET_PASSWORD"]
    os.environ["ORACLE_DSN"] = secrets["ORACLE_DSN"]
    os.environ["WALLET_ENCRIPTING_PASSWORD"] = secrets["WALLET_ENCRIPTING_PASSWORD"]

# read data from oracle, calculate statistics and save them back to oracle

load_generation = True
load_prices = True

country_codes = ["FR", "ES", "DE_LU"]
oracle_prices_table = "day_ahead_prices_raw"
oracle_generation_table = "generation_raw"
price_statistics_table = "prices_statistics"
generation_statistics_table = "generation_statistics"
start_date = "2026-09-06"
end_date = "2026-09-06"

connection = create_oracle_connection()
cursor = connection.cursor()

for country_code in country_codes:
    
    generation = read_data_from_oracle(
        connection, oracle_generation_table,country_code, start_date, end_date
    )

    if load_prices:
        prices = read_data_from_oracle(
            connection, oracle_prices_table,country_code, start_date, end_date)
        df = calculate_price_statistics(prices, generation)
        load_data_to_oracle(cursor, connection, df, price_statistics_table, f"{price_statistics_table}_staging")

    if load_generation:
        df = calculate_generation_statistics(generation)
        load_data_to_oracle(cursor, connection, df, generation_statistics_table, f"{generation_statistics_table}_staging", primary_keys = ["timestamp", "country_code", "generation_source"] )
