def create_table(cursor, data, table_name):

    database_lines = [
        "timestamp TIMESTAMP",
        "country_code VARCHAR2(10)",
    ]
    for column in data.columns:
        if column not in ["timestamp", "country_code", "generation_source", "generation_type"]:
            database_lines.append(f"{column} NUMBER")
        elif column in ["generation_source", "generation_type"]:
            database_lines.append(f"{column} VARCHAR2(100)")
        
    try:
        cursor.execute(f"DROP TABLE {table_name}")
    except:
        pass
    database_lines = ", ".join(database_lines)
    cursor.execute(f"""
                        CREATE TABLE {table_name} (
                            {database_lines}
                        )
                            
                        """)

if __name__ == '__main__':
    from download_yesterday_data import download_yesterday_data
    load, day_ahead_prices, generation_long = download_yesterday_data("ES")

    import oracledb
    import os

    if os.path.exists("login_information.py"):
        from login_information import (
            DB_DSN,
            DB_PASSWORD,
            DB_USER,
            WALLET_LOCATION,
            WALLET_PASSWORD,
        )

        os.environ["WALLET_LOCATION"] = WALLET_LOCATION
        os.environ["DB_USER"] = DB_USER
        os.environ["DB_PASSWORD"] = DB_PASSWORD
        os.environ["DB_DSN"] = DB_DSN
        os.environ["WALLET_PASSWORD"] = WALLET_PASSWORD

    connection=oracledb.connect(
        config_dir=os.environ["WALLET_LOCATION"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        dsn=os.environ["DB_DSN"],
        wallet_location=os.environ["WALLET_LOCATION"],
        wallet_password=os.environ["WALLET_PASSWORD"])
    
    cursor = connection.cursor()


    #create_table(cursor, load, "load_raw")
    #create_table(cursor, load, "load_staging")
    #create_table(cursor, day_ahead_prices, "day_ahead_prices_staging")
    create_table(cursor, generation_long, "generation_staging")

    #create_table(cursor, day_ahead_prices, "day_ahead_prices_raw")
    create_table(cursor, generation_long, "generation_raw")