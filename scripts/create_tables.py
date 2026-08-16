from src.etl.create_tables import create_table
from src.etl.download_yesterday_data import download_yesterday_data
from src.oracle_connection import create_oracle_connection

load, day_ahead_prices, generation_long = download_yesterday_data("ES")

connection = create_oracle_connection()
cursor = connection.cursor()


#create_table(cursor, load, "load_raw")
#create_table(cursor, load, "load_staging")
#create_table(cursor, day_ahead_prices, "day_ahead_prices_staging")
create_table(cursor, generation_long, "generation_staging")

#create_table(cursor, day_ahead_prices, "day_ahead_prices_raw")
create_table(cursor, generation_long, "generation_raw")