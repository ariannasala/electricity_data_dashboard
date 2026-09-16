from abc import ABC, abstractmethod
from datetime import datetime

from entsoe import EntsoePandasClient
from src.schemas import ColumnData


class DataTable:
    def __init__(self, data_name, columns_data):
        self.table_name = data_name
        self.data_name = data_name
        self.staging_table_name = data_name + "_staging"
        self.columns = columns_data
        self.columns_names = [cd.name for cd in columns_data]
        self.primary_keys = [cd.name for cd in columns_data if cd.primary_key]


class PrimaryTable(DataTable, ABC):
    def __init__(self, data_name, columns_data):
        self.client = EntsoePandasClient()
        super().__init__(data_name, columns_data)
        self.table_name = data_name + "_raw"

    @abstractmethod
    def download(self, countries: str | list[str], start_date, end_date):
        pass


class LoadTable(PrimaryTable):
    def __init__(self):
        super().__init__(
            "load",
            [
                ColumnData("timestamp", datetime, True),
                ColumnData("country_code", str, True),
                ColumnData("load", float, False),
            ],
        )

    def download(self, countries: str | list[str], start_date, end_date):
        from src.etl.download_electricity_data import download_data_from_entsoe

        load = download_data_from_entsoe(
            self.data_name,
            self.columns,
            self.client.query_load,
            countries,
            start_date,
            end_date,
        )

        load = load.rename(
            columns={
                "timestamp": "timestamp",
                "country_code": "country_code",
                "Actual Load": "load",
            }
        )
        load = load[[column_name for column_name in self.columns_names]].reset_index(
            drop=True
        )

        return load


class DayAheadPricesTable(PrimaryTable):
    def __init__(self):
        super().__init__(
            "day_ahead_prices",
            [
                ColumnData("timestamp", datetime, True),
                ColumnData("country_code", str, True),
                ColumnData("day_ahead_prices", float, False),
            ],
        )

    def download(self, countries: str | list[str], start_date, end_date):
        from src.etl.download_electricity_data import download_data_from_entsoe

        prices = download_data_from_entsoe(
            self.data_name,
            self.columns,
            self.client.query_day_ahead_prices,
            countries,
            start_date,
            end_date,
        )

        prices = prices.rename(
            columns={
                "timestamp": "timestamp",
                "country_code": "country_code",
                "Actual Load": "load",
            }
        )
        prices = prices[
            [column_name for column_name in self.columns_names]
        ].reset_index(drop=True)

        return prices


class GenerationTable(PrimaryTable):
    def __init__(self):
        super().__init__(
            "generation",
            [
                ColumnData("timestamp", datetime, True),
                ColumnData("country_code", str, True),
                ColumnData("generation_source", str, True),
                ColumnData("generation_type", str, True),
                ColumnData("generation", float, False),
            ],
        )

    def download(self, countries: str | list[str], start_date, end_date):
        from src.etl.download_electricity_data import download_data_from_entsoe

        generation = download_data_from_entsoe(
            self.data_name,
            self.columns,
            self.client.query_generation,
            countries,
            start_date,
            end_date,
        )

        generation_long = (
            generation.set_index(["timestamp", "country_code"])
            .stack([0, 1])
            .reset_index()
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
        generation_long = generation_long[self.columns_names]
        # we may have cathegories only for some countries, so we fill nans with zeros
        generation_long = generation_long.fillna(0)

        return generation_long


BASIC_STATISTICS_COLUMNS = [
    ColumnData("average", float),
    ColumnData("maximum", float),
    ColumnData("minimum", float),
    ColumnData("standard_deviation", float),
    ColumnData("maximum_price_hour", float),
    ColumnData("minimum_price_hour", float),
    ColumnData("p90", float),
    ColumnData("p10", float),
    ColumnData("p95", float),
    ColumnData("p05", float),
    ColumnData("p99", float),
    ColumnData("p01", float),
]


class PriceStatisticsTable(DataTable):
    def __init__(self):
        super().__init__(
            "prices_statistics",
            [
                ColumnData("timestamp", datetime, True),
                ColumnData("country_code", str, True),
            ]
            + BASIC_STATISTICS_COLUMNS
            + [
                ColumnData("number_negative_hours", float),
                ColumnData("solar_capture_price", float),
                ColumnData("wind_capture_price", float),
            ],
        )


class GenerationStatisticsTable(DataTable):
    def __init__(self):
        super().__init__(
            "generation_statistics",
            [
                ColumnData("timestamp", datetime, True),
                ColumnData("country_code", str, True),
                ColumnData("generation_source", str, True),
                ColumnData("cathegory", str, True),
            ]
            + BASIC_STATISTICS_COLUMNS
            + [
                ColumnData("sum", float),
            ],
        )
