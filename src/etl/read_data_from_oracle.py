import numpy as np
import pandas as pd

MINIMUM_GENERATION_DERIVATIVE = 15000

def read_data_from_oracle(connection, table_name, date, country):
    sql = f"""
    SELECT * FROM {table_name}
    WHERE timestamp >= TIMESTAMP '{date} 00:00:00'
    AND timestamp <= TIMESTAMP '{date} 23:59:59'
    AND country_code = '{country}'
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

def _transform_generation_data(raw_generation):
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

    generation_pivot = generation.pivot(
        index="TIMESTAMP", columns="SOURCE", values="GENERATION"
    ).reset_index()

    # we check the derivative to fill very short glitches in the data
    derivative = generation_pivot.drop(columns = ["TIMESTAMP"]).sum(axis=1).diff()
    is_glitch = (derivative < - MINIMUM_GENERATION_DERIVATIVE) & (
        derivative.shift(-1) > MINIMUM_GENERATION_DERIVATIVE)

    generation_pivot.loc[is_glitch, generation_pivot.columns] = np.nan
    generation_pivot = generation_pivot.interpolate()

    columns_zero_sum = generation_pivot.drop(columns=["TIMESTAMP"]).columns[
            generation_pivot.drop(columns=["TIMESTAMP"]).sum(axis=0) == 0
    ]
    generation_pivot = generation_pivot.drop(columns=columns_zero_sum)

    return generation_pivot


def get_and_trasform_data(connection, selected_date, selected_country):
    load = read_data_from_oracle(
        connection, "load_raw", selected_date, selected_country
    )
    day_ahead_prices = read_data_from_oracle(
        connection, "day_ahead_prices_raw", selected_date, selected_country
    )
    generation = read_data_from_oracle(
        connection, "generation_raw", selected_date, selected_country
    )

    generation_pivot = _transform_generation_data(generation)
    

    return load, day_ahead_prices, generation_pivot    