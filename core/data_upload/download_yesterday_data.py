from datetime import datetime, date, timedelta
from entsoe import EntsoePandasClient
import pandas as pd
import os

COUNTRY_CODE = os.environ["COUNTRY_CODE"]
client = EntsoePandasClient(api_key=os.environ["ENTSOE_API_KEY"])


def download_yesterday_data(country_code):
    """
    Downloads data from entsoe for yesterday.
    Specifically, load, day_ahead_prices and generation. Generation is turned to the long format.

    Parameters
    -----------
    coutry_code : str
        The country code to download data for.
    """
    yesterday = date.today() - timedelta(days=1)

    start = pd.Timestamp(
        datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0),
        tz="Europe/Brussels",
    )
    end = pd.Timestamp(
        datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59),
        tz="Europe/Brussels",
    )

    load = client.query_load(country_code, start=start, end=end)
    day_ahead_prices = pd.DataFrame(
        client.query_day_ahead_prices(country_code, start=start, end=end),
        columns=["day_ahead_prices"],
    )
    generation = client.query_generation(country_code, start=start, end=end)

    load["country_code"] = country_code
    day_ahead_prices["country_code"] = country_code
    generation["country_code"] = country_code

    load["timestamp"] = load.index
    day_ahead_prices["timestamp"] = day_ahead_prices.index
    generation["timestamp"] = generation.index

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
