import pandas as pd


def create_table(cursor, data, table_name):
    """
    Creates a table in the database.
    """
    database_lines = []
    for column in data.columns:
        if pd.api.types.is_datetime64_any_dtype(data[column]):
            database_lines.append(f"{column} TIMESTAMP")
        if pd.api.types.is_numeric_dtype(data[column]):
            database_lines.append(f"{column} NUMBER")
        elif pd.api.types.is_string_dtype(data[column]):
            database_lines.append(f"{column} VARCHAR2(100)")

    database_lines = ", ".join(database_lines)
    cursor.execute(
        f"""
        CREATE TABLE {table_name} (
            {database_lines}
        )
            
        """
    )
