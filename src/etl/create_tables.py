from datetime import datetime

from src.etl.tables import DataTable


def create_table(cursor, table: DataTable):
    """
    Creates a table in the database.
    """
    database_lines = []
    for column in table.columns:
        if column.data_type is datetime:
            database_lines.append(f"{column} TIMESTAMP")
        elif column.data_type in (float, int):
            database_lines.append(f"{column} NUMBER")
        elif column.data_type is str:
            database_lines.append(f"{column} VARCHAR2(100)")

    database_lines = ", ".join(database_lines)

    for table_name in [table.table_name, table.staging_table_name]:
        cursor.execute(
            f"""
            CREATE TABLE {table_name} (
                {database_lines}
            )
                
            """
        )
