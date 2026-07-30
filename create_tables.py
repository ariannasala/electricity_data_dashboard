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

    import login_information as info
    import oracledb

    connection=oracledb.connect(
         config_dir=info.wallet_location,
         user=info.user,
         password=info.password,
         dsn=info.cs,
         wallet_location=info.wallet_location,
         wallet_password=info.wallet_password)
    
    cursor = connection.cursor()


    #create_table(cursor, load, "load_raw")
    #create_table(cursor, load, "load_staging")
    #create_table(cursor, day_ahead_prices, "day_ahead_prices_staging")
    create_table(cursor, generation_long, "generation_staging")

    #create_table(cursor, day_ahead_prices, "day_ahead_prices_raw")
    create_table(cursor, generation_long, "generation_raw")