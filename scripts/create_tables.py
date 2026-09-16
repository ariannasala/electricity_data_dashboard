import os

from src.etl.create_tables import create_table
from src.oracle_connection import create_oracle_connection

from src.etl.tables import (
    DayAheadPricesTable,
    GenerationTable,
    LoadTable,
    PriceStatisticsTable,
    GenerationStatisticsTable,
)

## INPUTS
table_to_create = LoadTable()  # use the table you want to create
###

if not os.environ.get("ENTSOE_API_KEY"):
    from streamlit import secrets

    os.environ["ENTSOE_API_KEY"] = secrets["ENTSOE_API_KEY"]


connection = create_oracle_connection()
cursor = connection.cursor()

# create_table(cursor, price_statistics, "prices_statistics")
# create_table(cursor,price_statistics, "prices_statistics_staging")

create_table(cursor, table_to_create)


connection.commit()

connection.close()
