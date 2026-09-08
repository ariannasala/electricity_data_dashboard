import numpy as np
import pandas as pd

def read_data_from_oracle(connection, table_name, country_code, date_start, date_end=None):
    if date_end is None:
        date_end = date_start
    sql = f"""
    SELECT * FROM {table_name}
    WHERE timestamp >= TIMESTAMP '{date_start} 00:00:00'
    AND timestamp <= TIMESTAMP '{date_end} 23:59:59'
    AND country_code = '{country_code}'
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


def get_available_countries(connection, table_name):
    sql = f"""
    SELECT DISTINCT country_code FROM {table_name} ORDER BY country_code
    """
    available_countries = pd.read_sql(sql, connection)["COUNTRY_CODE"].tolist()

    return available_countries

def transform_generation_data(raw_generation):
    from src.utils import get_generation_category

    actual_consumption_indices = raw_generation[
            raw_generation["GENERATION_TYPE"] == "Actual Consumption"
        ].index
        
    generation = raw_generation.copy()

    generation.loc[actual_consumption_indices, "GENERATION"] = (
        generation.loc[actual_consumption_indices, "GENERATION"] * -1
    )
    generation["SOURCE"] = (
        generation["GENERATION_TYPE"] + " " + generation["GENERATION_SOURCE"]
    )
    generation["SOURCE"] = generation["SOURCE"].str.replace(
        "Actual Aggregated ", "", regex=False
    )
    
    #generation["CATHEGORY"] = generation["SOURCE"].apply(get_generation_category)

    #generation_pivot = generation.pivot(
    #    index="TIMESTAMP", columns=["SOURCE", "CATHEGORY"], values="GENERATION"
    #).reset_index()

    generation_pivot = generation.pivot(
            index="TIMESTAMP", columns=["SOURCE"], values="GENERATION"
        ).reset_index()

    # we check the derivative to fill very short glitches in the dat
    columns_zero_sum = generation_pivot.drop(columns=["TIMESTAMP"]).columns[
            generation_pivot.drop(columns=["TIMESTAMP"]).sum(axis=0) == 0
    ]
    generation_pivot = generation_pivot.drop(columns=columns_zero_sum)
    generation_pivot = _resample_dataframe(generation_pivot)

    return generation_pivot

def _resample_dataframe(df):
    frequency = pd.to_timedelta(df["TIMESTAMP"].diff().mode()).iloc[0]
    df = df.set_index("TIMESTAMP").resample(frequency).asfreq().reset_index()

    return df
def get_data_for_dashboard(connection, selected_date, selected_country_code):
    load = _resample_dataframe(read_data_from_oracle(
        connection, "load_raw", selected_country_code, selected_date, 
    ))
    
    day_ahead_prices = _resample_dataframe(read_data_from_oracle(
        connection, "day_ahead_prices_raw", selected_country_code, selected_date, 
    ))
    generation = read_data_from_oracle(
        connection, "generation_raw", selected_country_code, selected_date, 
    )

    return load, day_ahead_prices, generation  