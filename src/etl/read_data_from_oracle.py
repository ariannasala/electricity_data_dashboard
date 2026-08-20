
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

def get_and_trasform_data(connection, selected_date):
    load = read_data_from_oracle(connection, "load_raw", selected_date)
    day_ahead_prices = read_data_from_oracle(
        connection, "day_ahead_prices_raw", selected_date
    )
    generation = read_data_from_oracle(
        connection, 
        "generation_raw", 
        selected_date)
    actual_consumption_indices = generation[generation["GENERATION_TYPE"] == "Actual Consumption"].index
    generation.loc[actual_consumption_indices, "GENERATION"] = generation.loc[actual_consumption_indices, "GENERATION"] * -1
    generation["SOURCE"] = generation["GENERATION_TYPE"] + " " + generation["GENERATION_SOURCE"]
    generation["SOURCE"] = generation["SOURCE"].str.replace("Actual Aggregated", "", regex=False)

    generation_pivot = generation.pivot(index="TIMESTAMP", columns="SOURCE", values="GENERATION").reset_index()
    columns_zero_sum = generation_pivot.drop(columns=["TIMESTAMP"]).columns[generation_pivot.drop(columns=["TIMESTAMP"]).sum(axis=0) == 0]
    generation_pivot = generation_pivot.drop(columns=columns_zero_sum)

    return load, day_ahead_prices, generation_pivot