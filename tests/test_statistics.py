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
