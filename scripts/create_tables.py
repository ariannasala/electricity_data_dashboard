import os
import pandas as pd
from datetime import datetime, timedelta, timezone

from src.etl.create_tables import create_table
from src.etl.download_electricity_data import download_electricity_data
from src.oracle_connection import create_oracle_connection
from src.statistics.daily_statistics import calculate_price_statistics, calculate_generation_statistics

if not os.environ.get("ENTSOE_API_KEY"):
    from streamlit import secrets
    os.environ["ENTSOE_API_KEY"] = secrets["ENTSOE_API_KEY"]


yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)

load, day_ahead_prices, generation_long = download_electricity_data(
    "Spain", start_date=yesterday, end_date=yesterday
)



price_statistics = calculate_price_statistics(day_ahead_prices, generation_long)
generation_statistics = calculate_generation_statistics(generation_long)

connection = create_oracle_connection()

cursor = connection.cursor()


#create_table(cursor, price_statistics, "prices_statistics")
#create_table(cursor,price_statistics, "prices_statistics_staging")

create_table(cursor, generation_statistics, "generation_statistics")
create_table(cursor, generation_statistics, "generation_statistics_staging")


connection.commit()

connection.close()