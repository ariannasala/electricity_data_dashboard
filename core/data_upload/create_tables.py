def create_table(cursor, data, table_name):
    """
    Creates a table in the database.
    """
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
        print (f"Table {table_name} dropped.")
    except:
        print (f"Table {table_name} cannot be dropped - probably it does not exist.")
    database_lines = ", ".join(database_lines)
    cursor.execute(f"""
                        CREATE TABLE {table_name} (
                            {database_lines}
                        )
                            
                        """)