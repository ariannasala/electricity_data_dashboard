import pandas as pd
from src.schemas import COUNTRIES, COUNTRY_CODES
from src.utils import get_generation_category

MISSING_VALUES = -99999


def _timestamps_in_country_timezone(timestamps, timezone_name):
    def normalize_timestamp(timestamp):
        parsed_timestamp = pd.Timestamp(timestamp)
        if parsed_timestamp.tzinfo is None:
            return parsed_timestamp.tz_localize(timezone_name)
        return parsed_timestamp.tz_convert(timezone_name)

    return pd.to_datetime(timestamps.map(normalize_timestamp))


def _timestamps_in_utc(timestamps, timezone_name):
    return pd.to_datetime(
        _timestamps_in_country_timezone(timestamps, timezone_name), utc=True
    )


def _dataframe_with_utc_timestamps(dataframe):
    dataframe_with_utc_timestamps = dataframe.copy()
    normalized_timestamps = []

    for country_code, country_data in dataframe.groupby("country_code"):
        timezone_name = COUNTRIES[COUNTRY_CODES[country_code]].timezone
        normalized_timestamps.append(
            _timestamps_in_utc(country_data["timestamp"], timezone_name)
        )

    if normalized_timestamps:
        dataframe_with_utc_timestamps["timestamp_utc"] = pd.concat(
            normalized_timestamps
        ).sort_index()
    else:
        dataframe_with_utc_timestamps["timestamp_utc"] = pd.to_datetime(
            dataframe_with_utc_timestamps["timestamp"], utc=True
        )

    return dataframe_with_utc_timestamps


def _add_day_to_the_dataframe(dataframe):
    dataframe_with_day = dataframe.copy()
    dataframe_with_day["day"] = pd.NA
    local_timestamps = []

    for country_code, country_data in dataframe.groupby("country_code"):
        timezone_name = COUNTRIES[COUNTRY_CODES[country_code]].timezone
        timestamp_right_zone = _timestamps_in_country_timezone(
            country_data["timestamp"], timezone_name
        )
        local_timestamps.append(timestamp_right_zone)
        day = timestamp_right_zone.dt.date
        dataframe_with_day.loc[country_data.index, "day"] = day

    if local_timestamps:
        dataframe_with_day["timestamp_local"] = pd.concat(
            local_timestamps
        ).sort_index()
    else:
        dataframe_with_day["timestamp_local"] = pd.to_datetime(
            dataframe_with_day["timestamp"]
        )

    return dataframe_with_day


def _calculate_basic_statistics(groupby, column_name):
    average = groupby.mean()[column_name].rename("average")
    maximum = groupby.max()[column_name].rename("maximum")
    minimum = groupby.min()[column_name].rename("minimum")
    standard_deviation = groupby.std()[column_name].rename("standard_deviation")
    p90 = groupby.quantile(0.90)[column_name].rename("p90")
    p10 = groupby.quantile(0.10)[column_name].rename("p10")
    p95 = groupby.quantile(0.95)[column_name].rename("p95")
    p05 = groupby.quantile(0.05)[column_name].rename("p05")
    p99 = groupby.quantile(0.99)[column_name].rename("p99")
    p01 = groupby.quantile(0.01)[column_name].rename("p01")

    return pd.concat(
        [
            average,
            maximum,
            minimum,
            standard_deviation,
            p90,
            p10,
            p95,
            p05,
            p99,
            p01,
        ],
        axis=1,
    )


def calculate_price_statistics(prices, generation_data):
    # convert to lowercase to make this work with the data read from oracle as well as the data read from entsoe
    prices.columns = prices.columns.str.lower()
    generation_data.columns = generation_data.columns.str.lower()

    # check if the dataframes are empty
    if len(prices) == 0 or len(generation_data) == 0:
        raise ValueError(
            "Prices or generation data is empty, cannot calculate statistics."
        )

    resampled_prices_list = []
    prices = _add_day_to_the_dataframe(prices)

    maximum_price_hours = []
    minimum_price_hours = []
    for country_code, country_prices in prices.groupby("country_code"):
        # we need to resample to hourly to get the right number of negative hours
        timezone_name = COUNTRIES[COUNTRY_CODES[country_code]].timezone
        local_timestamp_index = pd.DatetimeIndex(
            country_prices["timestamp_local"].tolist(), name="timestamp_local"
        )

        resampled_prices = (
            country_prices.set_index(local_timestamp_index)[
                "day_ahead_prices"
            ]
            .resample("h")
            .mean()
            .reset_index()
            .rename(columns={"timestamp_local": "timestamp"})
        )
        resampled_prices["country_code"] = country_code
        resampled_prices_list.append(_add_day_to_the_dataframe(resampled_prices))

        # now we get the maximum price hour - we need to do it here because we need to get the right timezone for each country
        groupby = country_prices.groupby(["day"])

        maximum_price_time = (
            country_prices.loc[groupby.idxmax()["day_ahead_prices"]]
            .groupby(["day"])
            .first()["timestamp_local"]
        )
        minimum_price_time = (
            country_prices.loc[groupby.idxmin()["day_ahead_prices"]]
            .groupby(["day"])
            .first()["timestamp_local"]
        )

        maximum_price_time = pd.to_datetime(maximum_price_time)
        minimum_price_time = pd.to_datetime(minimum_price_time)
        maximum_price_hour = (maximum_price_time.dt.hour * 60) + maximum_price_time.dt.minute
        minimum_price_hour = (minimum_price_time.dt.hour * 60) + minimum_price_time.dt.minute
        country_code_series = [country_code] * len(maximum_price_hour)

        maximum_price_hour.index = pd.MultiIndex.from_arrays(
            [
                country_code_series,
                maximum_price_hour.index,
            ],
            names=["country_code", "day"],
        )
        minimum_price_hour.index = pd.MultiIndex.from_arrays(
            [
                country_code_series,
                minimum_price_hour.index,
            ],
            names=["country_code", "day"],
        )

        maximum_price_hours.append(maximum_price_hour)
        minimum_price_hours.append(minimum_price_hour)

    resampled_prices = pd.concat(resampled_prices_list)
    groupby = prices.groupby(["country_code", "day"])[["day_ahead_prices"]]
    basic_statistics = _calculate_basic_statistics(groupby, "day_ahead_prices")

    maximum_price_hour = pd.concat(maximum_price_hours, axis=0).rename(
        "maximum_price_hour"
    )
    minimum_price_hour = pd.concat(minimum_price_hours, axis=0).rename(
        "minimum_price_hour"
    )
    number_negative_hours = (
        resampled_prices[resampled_prices["day_ahead_prices"] <= 0]
        .groupby(["country_code", "day"])
        .count()["day_ahead_prices"]
        .astype(int)
        .rename("number_negative_hours")
    )

    solar_generation = generation_data[generation_data["generation_source"] == "Solar"]
    solar_generation = _dataframe_with_utc_timestamps(solar_generation)
    prices_for_merge = _dataframe_with_utc_timestamps(prices)
    solar_generation_price = pd.merge(
        solar_generation,
        prices_for_merge,
        on=["country_code", "timestamp_utc"],
        how="inner",
    )
    solar_generation_price["product"] = (
        solar_generation_price["generation"]
        * solar_generation_price["day_ahead_prices"]
    )
    grouped_solar = solar_generation_price.groupby(["country_code", "day"])[
        ["product", "generation"]
    ]
    solar_capture_price = (
        grouped_solar.sum()["product"] / grouped_solar.sum()["generation"]
    ).rename("solar_capture_price")

    wind_generation = generation_data[
        generation_data["generation_source"].str.contains("Wind")
    ]
    wind_generation = _dataframe_with_utc_timestamps(wind_generation)
    wind_generation_price = pd.merge(
        wind_generation,
        prices_for_merge,
        on=["country_code", "timestamp_utc"],
        how="inner",
    )
    wind_generation_price["product"] = (
        wind_generation_price["generation"] * wind_generation_price["day_ahead_prices"]
    )
    grouped_wind = wind_generation_price.groupby(["country_code", "day"])[
        ["product", "generation"]
    ]
    wind_capture_price = (
        grouped_wind.sum()["product"] / grouped_wind.sum()["generation"]
    ).rename("wind_capture_price")

    dataframe = pd.concat(
        [
            basic_statistics,
            maximum_price_hour,
            minimum_price_hour,
            number_negative_hours,
            solar_capture_price,
            wind_capture_price,
        ],
        axis=1,
    )
    final_dataframe = dataframe.reset_index().rename(columns={"day": "timestamp"})[
        [
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
            "wind_capture_price",
        ]
    ]

    final_dataframe["timestamp"] = pd.to_datetime(final_dataframe["timestamp"])
    final_dataframe.loc[
        final_dataframe["number_negative_hours"].isna(), "number_negative_hours"
    ] = 0
    final_dataframe = final_dataframe.fillna(MISSING_VALUES)

    return final_dataframe


def calculate_generation_statistics(generation_long):
    # convert to lowercase to make this work with the data read from oracle as well as the data read from entsoe
    generation_long.columns = generation_long.columns.str.lower()

    generation_long["timestamp"] = pd.to_datetime(generation_long["timestamp"])
    generation_long = _add_day_to_the_dataframe(generation_long)
    generation_only_positive = generation_long[generation_long["generation_type"] != "Actual Consumption"]
    generation_only_positive["cathegory"] = generation_only_positive["generation_source"].apply(get_generation_category)


    groupby = generation_only_positive.groupby(["day", "country_code", "generation_source", "cathegory"])[
        ["generation"]
    ]
    basic_statistics = _calculate_basic_statistics(groupby, "generation")

    total_generation = groupby.sum()["generation"].rename("sum")

    final_dataframe = (
        pd.concat([basic_statistics, total_generation], axis=1)
        .reset_index()
        .rename(columns={"day": "timestamp"})
    )

    final_dataframe["timestamp"] = pd.to_datetime(final_dataframe["timestamp"])

    return final_dataframe
