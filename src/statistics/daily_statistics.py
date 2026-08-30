import pandas as pd
from src.schemas import COUNTRIES, COUNTRY_CODES

MISSING_VALUES = -99999

def calculate_price_statistics(prices, generation_data):

    prices["day"] = pd.NA
    for country_code, country_prices in prices.groupby("country_code"):

        datetime = pd.to_datetime(country_prices["timestamp"], utc = True)
        timezone_name = COUNTRIES[COUNTRY_CODES[country_code]].timezone
        timestamp_right_zone = datetime.dt.tz_convert(timezone_name)
        day = timestamp_right_zone.dt.date
        prices.loc[country_prices.index, "day"] = day

    groupby = prices.groupby(["country_code", "day"])[["day_ahead_prices"]]

    average = groupby.mean()["day_ahead_prices"].rename("average")

    maximum = groupby.max()["day_ahead_prices"].rename("maximum")
    minimum = groupby.min()["day_ahead_prices"].rename("minimum")

    maximum_price_time = (
        prices.loc[groupby.idxmax()["day_ahead_prices"]]
        .groupby(["country_code", "day"])
        .first()["timestamp"]
    )
    minimum_price_time = (
        prices.loc[groupby.idxmin()["day_ahead_prices"]]
        .groupby(["country_code", "day"])
        .first()["timestamp"]
    )

    maximum_price_hour = (
        (pd.to_datetime(maximum_price_time).dt.hour * 60)
        + pd.to_datetime(maximum_price_time).dt.minute
    ).rename("maximum_price_hour")
    minimum_price_hour = (
        (pd.to_datetime(minimum_price_time).dt.hour * 60)
        + pd.to_datetime(minimum_price_time).dt.minute
    ).rename("minimum_price_hour")

    standard_deviation = groupby.std()["day_ahead_prices"].rename("standard_deviation")
    p90 = groupby.quantile(0.90)["day_ahead_prices"].rename("p90")
    p10 = groupby.quantile(0.10)["day_ahead_prices"].rename("p10")
    p95 = groupby.quantile(0.95)["day_ahead_prices"].rename("p95")
    p05 = groupby.quantile(0.05)["day_ahead_prices"].rename("p05")
    p99 = groupby.quantile(0.99)["day_ahead_prices"].rename("p99")
    p01 = groupby.quantile(0.01)["day_ahead_prices"].rename("p01")

    number_negative_hours = (
        prices[prices["day_ahead_prices"] <= 0]
        .groupby(["country_code", "day"])
        .count()["day_ahead_prices"]
        .rename("number_negative_hours")
    )

    solar_generation = generation_data[generation_data["generation_source"] == "Solar"]
    solar_generation_price = pd.merge(
        solar_generation, prices, on=["country_code", "timestamp"], how="inner"
    )
    solar_generation_price["product"] = (
        solar_generation_price["generation"]
        * solar_generation_price["day_ahead_prices"]
    )
    grouped_solar = solar_generation_price.groupby(["country_code", "day"])[["product", "generation"]]
    solar_capture_price = (
        grouped_solar.sum()["product"] / grouped_solar.sum()["generation"]
    ).rename("solar_capture_price")

    wind_generation = generation_data[
        generation_data["generation_source"].str.contains("Wind")
    ]
    wind_generation_price = pd.merge(
        wind_generation, prices, on=["country_code", "timestamp"], how="inner"
    )
    wind_generation_price["product"] = (
        wind_generation_price["generation"] * wind_generation_price["day_ahead_prices"]
    )
    grouped_wind = wind_generation_price.groupby(["country_code", "day"])[["product", "generation"]]
    wind_capture_price = (
        grouped_wind.sum()["product"] / grouped_wind.sum()["generation"]
    ).rename("wind_capture_price")

    dataframe = pd.concat(
        [   
            average,
            maximum,
            minimum,
            standard_deviation,
            maximum_price_hour,
            minimum_price_hour,
            p90,
            p10,
            p95,
            p05,
            p99,
            p01,
            number_negative_hours,
            solar_capture_price,
            wind_capture_price,
        ],
        axis=1,
    )
    final_dataframe = dataframe.reset_index().rename(columns={"day": "timestamp"})[[
        "timestamp",
        "country_code",
        "average",
        "maximum",
        "minimum",
        "standard_deviation",
        "maximum_price_hour",
        "minimum_price_hour",
        "p90",
        "p10",
        "p95",
        "p05",
        "p99",
        "p01",
        "number_negative_hours",
        "solar_capture_price",
        "wind_capture_price",]
    ]

    final_dataframe["timestamp"] = pd.to_datetime(final_dataframe["timestamp"])
    final_dataframe.loc[
        final_dataframe["number_negative_hours"].isna(), "number_negative_hours"
    ] = 0
    final_dataframe = final_dataframe.fillna(MISSING_VALUES)

    return final_dataframe
