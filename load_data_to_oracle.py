def load_data_to_oracle(
    cursor,
    connection,
    data,
    table_name,
    staging_table_name,
    primary_keys=["timestamp", "country_code"],
):
    rows = list(data.itertuples(index=False, name=None))

    number_of_columns = len(data.columns)
    list_of_columns = [f":{i}" for i in range(1, number_of_columns + 1)]

    cursor.execute("TRUNCATE TABLE " + staging_table_name)

    sql = f"""
    INSERT INTO {staging_table_name}
    VALUES ({",".join(list_of_columns)})
    """

    cursor.executemany(sql, rows)

    connection.commit()

    update_clause = ",\n".join(
        f"t.{column}=s.{column}"
        for column in data.columns
        if column not in primary_keys
    )

    on_clause = " AND ".join(f"t.{column}=s.{column}" for column in primary_keys)

    insert_values = ", ".join(f"s.{column}" for column in data.columns)
    insert_columns = ", ".join(data.columns)

    merge_sql = f"""
    MERGE INTO {table_name} t
    USING {staging_table_name} s
    ON ({on_clause})
    WHEN MATCHED THEN
        UPDATE SET
            {update_clause}
    WHEN NOT MATCHED THEN
        INSERT ({insert_columns})
        VALUES ({insert_values})
    """

    cursor.execute(merge_sql)
    connection.commit()


def main():
    from download_yesterday_data import download_yesterday_data

    import login_information as info
    import oracledb

    load, day_ahead_prices, generation_long = download_yesterday_data("ES")

    connection = oracledb.connect(
        config_dir=info.wallet_location,
        user=info.user,
        password=info.password,
        dsn=info.cs,
        wallet_location=info.wallet_location,
        wallet_password=info.wallet_password,
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


if __name__ == "__main__":
    main()
