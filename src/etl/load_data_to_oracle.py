import pandas as pd

from src.etl.tables import DataTable


def load_data_to_oracle(
    connection,
    table: DataTable,
    data: pd.DataFrame,
):
    """
    Load data to oracle. The data is loaded to a staging table and then merged into the target table.
    """
    cursor = connection.cursor()
    primary_keys = (
        ["timestamp", "country_code"]
        if table.primary_keys is None
        else table.primary_keys
    )
    rows = list(data.itertuples(index=False, name=None))

    number_of_columns = len(data.columns)
    list_of_columns = [f":{i}" for i in range(1, number_of_columns + 1)]

    cursor.execute("TRUNCATE TABLE " + table.staging_table_name)

    sql = f"""
        INSERT INTO {table.staging_table_name}
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
        MERGE INTO {table.table_name} t
        USING {table.staging_table_name} s
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
