import os
from datetime import datetime

import pandas as pd
from entsoe import EntsoePandasClient


def download_electricity_data(country_codes: list[str], start_date: datetime, end_date: datetime):
    """
    Downloads data from entsoe between start_date and end_date.
    Specifically, load, day_ahead_prices and generation. Generation is turned to the long format.

    Parameters
    -----------
    coutry_code : list[str] | str
        List of country code to download data for - or a single country code
    start_date : datetime
        The start date to download data from.
    end_date : datetime
        The end date to download data from.

    Returns
    -----------
    load : pd.DataFrame
        The load data.
    day_ahead_prices : pd.DataFrame
        The day ahead prices.
    generation : pd.DataFrame
        The generation data.
    """
    if isinstance(country_codes, str):
        country_codes = [country_codes]

    client = EntsoePandasClient(api_key=os.environ["ENTSOE_API_KEY"])


    start = pd.Timestamp(
            year = start_date.year,
            month = start_date.month,
            day = start_date.day,
            hour = 0,
            minute = 0,
            second = 0,
        tz="Europe/Brussels",
    )
    end = pd.Timestamp(
            year = end_date.year,
            month = end_date.month,
            day = end_date.day,
            hour = 23,
            minute = 59,
            second = 59,
        tz="Europe/Brussels",
    )

    total_loads = []
    total_day_ahead_prices = []
    total_generation = []

    for country_code in country_codes:
        load = client.query_load(country_code, start=start, end=end)
        day_ahead_prices = pd.DataFrame(
            client.query_day_ahead_prices(country_code, start=start, end=end),
            columns=["day_ahead_prices"],
        )
        generation = client.query_generation(country_code, start=start, end=end)

        # add country code to table
        load["country_code"] = country_code
        day_ahead_prices["country_code"] = country_code
        generation["country_code"] = country_code

        total_loads.append(load)
        total_day_ahead_prices.append(day_ahead_prices)
        total_generation.append(generation)

    load = pd.concat(total_loads)
    day_ahead_prices = pd.concat(total_day_ahead_prices)
    generation = pd.concat(total_generation)

    # add timestamp column
    load["timestamp"] = load.index
    day_ahead_prices["timestamp"] = day_ahead_prices.index
    generation["timestamp"] = generation.index

    load["timestamp"] = pd.to_datetime(load["timestamp"], utc = True)
    day_ahead_prices["timestamp"] = pd.to_datetime(day_ahead_prices["timestamp"], utc = True)
    generation["timestamp"] = pd.to_datetime(generation["timestamp"], utc = True)


    generation_long = (
        generation.set_index(["timestamp", "country_code"]).stack([0, 1]).reset_index()
    )
    generation_long = generation_long.rename(
        columns={
            "timestamp": "timestamp",
            "country_code": "country_code",
            "level_2": "generation_source",
            "level_3": "generation_type",
            0: "generation",
        }
    )
    generation_long = generation_long[["timestamp", "country_code", "generation_source", "generation_type", "generation"]]
    generation_long = generation_long.fillna(0)
    load = load.rename(
        columns={
            "timestamp": "timestamp",
            "country_code": "country_code",
            "Actual Load": "load",
        }
    )
    load = load[["timestamp", "country_code", "load"]]

    day_ahead_prices = day_ahead_prices[["timestamp", "country_code", "day_ahead_prices"]]

    return load, day_ahead_prices, generation_long
