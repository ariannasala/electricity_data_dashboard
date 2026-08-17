
import pandas as pd

def read_data_from_oracle(connection, table_name, date, group_by = None):
    sql = f"""
    SELECT * FROM {table_name}
    WHERE timestamp >= TIMESTAMP '{date} 00:00:00'
    AND timestamp <= TIMESTAMP '{date} 23:59:59'
    ORDER BY timestamp ASC
    """
    df = pd.read_sql(sql, connection)
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])

    return df

def get_available_dates(connection, table_name):
    sql = f"""
    SELECT DISTINCT TO_CHAR(timestamp, 'YYYY-MM-DD') 
    AS date_string FROM {table_name}
    ORDER BY date_string DESC
    """
    available_dates = pd.read_sql(sql, connection)["DATE_STRING"].tolist()

    return available_dates