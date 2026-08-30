import pandas as pd
import pytest

from src.statistics.daily_statistics import calculate_price_statistics


@pytest.fixture
def prices():
    return pd.DataFrame(
        {
            "country_code": ["FR", "FR", "FR", "FR", "DE", "DE", "DE", "DE"],
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
                "DE",
                "DE",
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
            "generation": [2, 1, 2, 1, 1, 3, 1, 1],
        }
    )

@pytest.fixture
def statistics_from_real_data_single_day():
    prices = pd.read_csv("tests/data/day_ahead_prices_example.csv")
    generation = pd.read_csv("tests/data/generation_long_example.csv")

    dataframe = calculate_price_statistics(prices, generation)
    return dataframe

def test_statistics_are_calculated_per_country_and_day(prices, generation):
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
    assert dataframe.loc[("DE", "2026-08-19"), "maximum"] == 15
    assert dataframe.loc[("DE", "2026-08-20"), "minimum"] == -10

    assert dataframe.loc[("FR", "2026-08-19"), "solar_capture_price"] == pytest.approx(5)
    assert dataframe.loc[("DE", "2026-08-19"), "wind_capture_price"] == pytest.approx(10)


def test_missing_statistics_are_filled(prices, generation):
    dataframe = calculate_price_statistics(prices, generation).set_index(
        ["country_code", "timestamp"]
    )

    assert dataframe.loc[("FR", "2026-08-20"), "number_negative_hours"] == 0
    assert dataframe.loc[("FR", "2026-08-20"), "wind_capture_price"] == -99999
    assert dataframe.loc[("DE", "2026-08-19"), "solar_capture_price"] == -99999
    assert dataframe.loc[("DE", "2026-08-20"), "solar_capture_price"] == -99999
    assert dataframe.loc[("DE", "2026-08-20"), "wind_capture_price"] == -99999

def test_single_day_data_has_statistics_for_one_day(statistics_from_real_data_single_day):
    """This test checks that timezones are handled correctly when we process data for a single day, for multiple countries."""

    # in previous versions, we had a bug: when converting to utc timestamp, we converted hour 00 to 22 of the previous day
    # so we calculated statistics from the previous day based only on those hours
    # we check that does not happen checking the number of unique timestamps and length of the dataframe
    assert len(statistics_from_real_data_single_day) == 2
    assert len(statistics_from_real_data_single_day["country_code"].unique()) == 2
    assert len(statistics_from_real_data_single_day["timestamp"].unique()) == 1

def test_prices_hour_real_data_for_one_day(statistics_from_real_data_single_day):
    """We check that the hour of the minimum price and maximum prices correctly calculated and refer correctly to the time zone"""
    # for Spain, price is 0 first at 13 -> minimum_price_hour should be 13 * 60 = 780
    assert statistics_from_real_data_single_day.set_index(["country_code", "timestamp"]).loc[("ES", "2026-08-26"), "minimum_price_hour"] == 780
    # for Spain, price is first 214 at 00:45 -> maximum price hour should be 00 * 60 + 45 = 45
    assert statistics_from_real_data_single_day.set_index(["country_code", "timestamp"]).loc[("ES", "2026-08-26"), "maximum_price_hour"] == 45
    # for France, minimum price (110.56) at 13.45 -> minimum_price_hour should be 13 * 60 + 45 = 825
    assert statistics_from_real_data_single_day.set_index(["country_code", "timestamp"]).loc[("FR", "2026-08-26"), "minimum_price_hour"] == 825
    # for France, maximum price (110.56) at 19:45 -> maximum price hour should be 19 * 60 + 45 = 1185
    assert statistics_from_real_data_single_day.set_index(["country_code", "timestamp"]).loc[("FR", "2026-08-26"), "maximum_price_hour"] == 1185
