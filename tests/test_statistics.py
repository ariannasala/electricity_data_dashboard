import pandas as pd
import pytest

from src.statistics.daily_statistics import (
    calculate_price_statistics,
    calculate_generation_statistics,
)
import numpy as np


@pytest.fixture
def prices():
    return pd.DataFrame(
        {
            "country_code": [
                "FR",
                "FR",
                "FR",
                "FR",
                "DE_LU",
                "DE_LU",
                "DE_LU",
                "DE_LU",
            ],
            "timestamp": pd.to_datetime(
                [
                    "2026-08-19 00:00",
                    "2026-08-19 01:00",
                    "2026-08-20 00:00",
                    "2026-08-20 01:00",
                    "2026-08-19 00:00",
                    "2026-08-19 01:00",
                    "2026-08-20 00:00",
                    "2026-08-20 01:00",
                ]
            ),
            "day_ahead_prices": [10, -5, 20, 30, 5, 15, -10, 10],
        }
    )


@pytest.fixture
def generation():
    return pd.DataFrame(
        {
            "country_code": [
                "FR",
                "FR",
                "FR",
                "FR",
                "FR",
                "FR",
                "DE_LU",
                "DE_LU",
            ],
            "timestamp": pd.to_datetime(
                [
                    "2026-08-19 00:00",
                    "2026-08-19 01:00",
                    "2026-08-20 00:00",
                    "2026-08-20 01:00",
                    "2026-08-19 00:00",
                    "2026-08-19 01:00",
                    "2026-08-19 00:00",
                    "2026-08-19 01:00",
                ]
            ),
            "generation_source": [
                "Solar",
                "Solar",
                "Solar",
                "Solar",
                "Wind Onshore",
                "Wind Onshore",
                "Wind Onshore",
                "Wind Onshore",
            ],
            "generation_type": [
                "Actual Generation",
                "Actual Generation",
                "Actual Generation",
                "Actual Generation",
                "Actual Generation",
                "Actual Generation",
                "Actual Generation",
                "Actual Generation",
            ],
            "generation": [2, 1, 2, 1, 1, 3, 1, 1],
        }
    )


@pytest.fixture
def price_statistics_from_real_data_single_day():
    prices = pd.read_csv("tests/data/day_ahead_prices_example.csv")
    generation = pd.read_csv("tests/data/generation_long_example.csv")

    dataframe = calculate_price_statistics(prices, generation)
    return dataframe


def test_price_statistics_are_calculated_per_country_and_day(prices, generation):
    dataframe = calculate_price_statistics(prices, generation).set_index(
        ["country_code", "timestamp"]
    )

    assert dataframe.loc[("FR", "2026-08-19"), "maximum"] == 10
    assert dataframe.loc[("FR", "2026-08-19"), "minimum"] == -5
    assert dataframe.loc[("FR", "2026-08-19"), "maximum_price_hour"] == 0
    assert dataframe.loc[("FR", "2026-08-19"), "minimum_price_hour"] == 60
    assert dataframe.loc[("FR", "2026-08-19"), "number_negative_hours"] == 1

    assert dataframe.loc[("FR", "2026-08-20"), "maximum"] == 30
    assert dataframe.loc[("FR", "2026-08-20"), "minimum"] == 20
    assert dataframe.loc[("DE_LU", "2026-08-19"), "maximum"] == 15
    assert dataframe.loc[("DE_LU", "2026-08-20"), "minimum"] == -10

    assert dataframe.loc[("FR", "2026-08-19"), "solar_capture_price"] == pytest.approx(
        5
    )
    assert dataframe.loc[
        ("DE_LU", "2026-08-19"), "wind_capture_price"
    ] == pytest.approx(10)


def test_missing_price_statistics_are_filled(prices, generation):
    dataframe = calculate_price_statistics(prices, generation).set_index(
        ["country_code", "timestamp"]
    )

    assert dataframe.loc[("FR", "2026-08-20"), "number_negative_hours"] == 0
    assert dataframe.loc[("FR", "2026-08-20"), "wind_capture_price"] == -99999
    assert dataframe.loc[("DE_LU", "2026-08-19"), "solar_capture_price"] == -99999
    assert dataframe.loc[("DE_LU", "2026-08-20"), "solar_capture_price"] == -99999
    assert dataframe.loc[("DE_LU", "2026-08-20"), "wind_capture_price"] == -99999


def test_single_day_data_has_statistics_for_one_day(
    price_statistics_from_real_data_single_day,
):
    """This test checks that timezones are handled correctly when we process data for a single day, for multiple countries."""

    # in previous versions, we had a bug: when converting to utc timestamp, we converted hour 00 to 22 of the previous day
    # so we calculated statistics from the previous day based only on those hours
    # we check that does not happen checking the number of unique timestamps and length of the dataframe
    assert len(price_statistics_from_real_data_single_day) == 2
    assert len(price_statistics_from_real_data_single_day["country_code"].unique()) == 2
    assert len(price_statistics_from_real_data_single_day["timestamp"].unique()) == 1


def test_solar_wind_capture_price(price_statistics_from_real_data_single_day):
    # check with results from excel
    assert np.isclose(
        price_statistics_from_real_data_single_day.set_index(
            ["country_code", "timestamp"]
        ).loc[("ES", "2026-08-26"), "solar_capture_price"],
        22.9458997151438,
    )
    assert np.isclose(
        price_statistics_from_real_data_single_day.set_index(
            ["country_code", "timestamp"]
        ).loc[("ES", "2026-08-26"), "wind_capture_price"],
        90.7290993563407,
    )


def test_prices_hour_real_data_for_one_day(price_statistics_from_real_data_single_day):
    """We check that the hour of the minimum price and maximum prices correctly calculated and refer correctly to the time zone"""
    # for Spain, price is 0 first at 13 -> minimum_price_hour should be 13 * 60 = 780
    assert (
        price_statistics_from_real_data_single_day.set_index(
            ["country_code", "timestamp"]
        ).loc[("ES", "2026-08-26"), "minimum_price_hour"]
        == 780
    )
    # for Spain, price is first 214 at 00:45 -> maximum price hour should be 00 * 60 + 45 = 45
    assert (
        price_statistics_from_real_data_single_day.set_index(
            ["country_code", "timestamp"]
        ).loc[("ES", "2026-08-26"), "maximum_price_hour"]
        == 45
    )
    # for France, minimum price (110.56) at 13.45 -> minimum_price_hour should be 13 * 60 + 45 = 825
    assert (
        price_statistics_from_real_data_single_day.set_index(
            ["country_code", "timestamp"]
        ).loc[("FR", "2026-08-26"), "minimum_price_hour"]
        == 825
    )
    # for France, maximum price (110.56) at 19:45 -> maximum price hour should be 19 * 60 + 45 = 1185
    assert (
        price_statistics_from_real_data_single_day.set_index(
            ["country_code", "timestamp"]
        ).loc[("FR", "2026-08-26"), "maximum_price_hour"]
        == 1185
    )


def test_number_of_zero_price_hour_is_hourly(
    price_statistics_from_real_data_single_day,
):
    assert (
        price_statistics_from_real_data_single_day.set_index(
            ["country_code", "timestamp"]
        ).loc[("ES", "2026-08-26"), "number_negative_hours"]
        == 3
    )


@pytest.mark.parametrize(
    "timestamps",
    [
        [
            "2026-03-29 00:00",
            "2026-03-29 01:00",
            "2026-03-29 03:00",
        ],
        [
            "2026-03-29 00:00:00+01:00",
            "2026-03-29 01:00:00+01:00",
            "2026-03-29 03:00:00+02:00",
        ],
    ],
    ids=["naive-local", "timezone-aware"],
)
def test_price_statistics_handle_spring_dst_transition(timestamps):
    parsed_timestamps = pd.to_datetime(
        timestamps, utc=any("+" in timestamp for timestamp in timestamps)
    )
    prices = pd.DataFrame(
        {
            "country_code": ["FR"] * len(timestamps),
            "timestamp": parsed_timestamps,
            "day_ahead_prices": [10, 20, 30],
        }
    )
    generation = pd.DataFrame(
        {
            "country_code": ["FR"] * len(timestamps),
            "timestamp": parsed_timestamps,
            "generation_source": ["Solar"] * len(timestamps),
            "generation": [1, 1, 1],
        }
    )

    statistics = calculate_price_statistics(prices, generation).set_index(
        ["country_code", "timestamp"]
    )

    assert statistics.loc[("FR", "2026-03-29"), "maximum_price_hour"] == 180
    assert statistics.loc[("FR", "2026-03-29"), "number_negative_hours"] == 0


def test_price_statistics_handle_fall_dst_transition_with_aware_timestamps():
    timestamps = pd.to_datetime(
        [
            "2026-10-25 00:00:00+02:00",
            "2026-10-25 01:00:00+02:00",
            "2026-10-25 02:00:00+02:00",
            "2026-10-25 02:00:00+01:00",
            "2026-10-25 03:00:00+01:00",
        ],
        utc=True,
    )
    prices = pd.DataFrame(
        {
            "country_code": ["FR"] * len(timestamps),
            "timestamp": timestamps,
            "day_ahead_prices": [10, 20, -5, -10, 30],
        }
    )
    generation = pd.DataFrame(
        {
            "country_code": ["FR"] * len(timestamps),
            "timestamp": timestamps,
            "generation_source": ["Wind Onshore"] * len(timestamps),
            "generation": [1] * len(timestamps),
        }
    )

    statistics = calculate_price_statistics(prices, generation).set_index(
        ["country_code", "timestamp"]
    )

    assert statistics.loc[("FR", "2026-10-25"), "minimum_price_hour"] == 120
    assert statistics.loc[("FR", "2026-10-25"), "number_negative_hours"] == 2


def test_generation_statistics_are_calculated_per_country_and_day(generation):
    """Test that generation statistics are correctly grouped by country, day, and generation source."""
    dataframe = calculate_generation_statistics(generation).set_index(
        ["country_code", "timestamp", "generation_source"]
    )

    # Check FR Solar on 2026-08-19: values are [2, 1]
    assert dataframe.loc[("FR", "2026-08-19", "Solar"), "average"] == 1.5
    assert dataframe.loc[("FR", "2026-08-19", "Solar"), "maximum"] == 2
    assert dataframe.loc[("FR", "2026-08-19", "Solar"), "minimum"] == 1
    assert dataframe.loc[("FR", "2026-08-19", "Solar"), "sum"] == 3

    # Check FR Solar on 2026-08-20: values are [2, 1]
    assert dataframe.loc[("FR", "2026-08-20", "Solar"), "average"] == 1.5
    assert dataframe.loc[("FR", "2026-08-20", "Solar"), "sum"] == 3

    # Check FR Wind Onshore on 2026-08-19: values are [1, 3]
    assert dataframe.loc[("FR", "2026-08-19", "Wind Onshore"), "average"] == 2.0
    assert dataframe.loc[("FR", "2026-08-19", "Wind Onshore"), "maximum"] == 3
    assert dataframe.loc[("FR", "2026-08-19", "Wind Onshore"), "minimum"] == 1
    assert dataframe.loc[("FR", "2026-08-19", "Wind Onshore"), "sum"] == 4

    # Check DE_LU Wind Onshore on 2026-08-19: values are [1, 1]
    assert dataframe.loc[("DE_LU", "2026-08-19", "Wind Onshore"), "average"] == 1.0
    assert dataframe.loc[("DE_LU", "2026-08-19", "Wind Onshore"), "maximum"] == 1
    assert dataframe.loc[("DE_LU", "2026-08-19", "Wind Onshore"), "minimum"] == 1
    assert dataframe.loc[("DE_LU", "2026-08-19", "Wind Onshore"), "sum"] == 2


def test_generation_statistics_percentiles_are_calculated(generation):
    """Test that percentiles are correctly calculated for generation statistics."""
    dataframe = calculate_generation_statistics(generation).set_index(
        ["country_code", "timestamp", "generation_source"]
    )

    # For FR Solar on 2026-08-19: values are [2, 1]
    assert dataframe.loc[("FR", "2026-08-19", "Solar"), "p90"] == pytest.approx(1.9)
    assert dataframe.loc[("FR", "2026-08-19", "Solar"), "p10"] == pytest.approx(1.1)
    assert dataframe.loc[("FR", "2026-08-19", "Solar"), "p95"] == pytest.approx(1.95)
    assert dataframe.loc[("FR", "2026-08-19", "Solar"), "p05"] == pytest.approx(1.05)


def test_generation_statistics_standard_deviation_is_calculated(generation):
    """Test that standard deviation is correctly calculated for generation statistics."""
    dataframe = calculate_generation_statistics(generation).set_index(
        ["country_code", "timestamp", "generation_source"]
    )

    # For FR Solar on 2026-08-19: values are [2, 1], sample std (N-1) should be sqrt(0.5) ≈ 0.707
    assert dataframe.loc[
        ("FR", "2026-08-19", "Solar"), "standard_deviation"
    ] == pytest.approx(0.7071067811865476)

    # For FR Wind Onshore on 2026-08-19: values are [1, 3], sample std (N-1) should be sqrt(2) ≈ 1.414
    assert dataframe.loc[
        ("FR", "2026-08-19", "Wind Onshore"), "standard_deviation"
    ] == pytest.approx(1.4142135623730951)


def test_generation_statistics_from_real_data():
    """Test that generation statistics are correctly calculated from real data for multiple days and countries."""
    generation = pd.read_csv("tests/data/generation_long_example.csv")

    dataframe = calculate_generation_statistics(generation)

    # Check that we have statistics for multiple countries and generation sources
    assert len(dataframe) > 0
    assert "country_code" in dataframe.columns
    assert "timestamp" in dataframe.columns
    assert "generation_source" in dataframe.columns
    assert "average" in dataframe.columns
    assert "maximum" in dataframe.columns
    assert "minimum" in dataframe.columns
    assert "sum" in dataframe.columns

    # Check that timestamps are datetime objects
    assert pd.api.types.is_datetime64_any_dtype(dataframe["timestamp"])

    # Check that each row has at least one country, one timestamp, and one generation source
    assert len(dataframe["country_code"].unique()) >= 1
    assert len(dataframe["timestamp"].unique()) >= 1
