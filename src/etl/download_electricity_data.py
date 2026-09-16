from entsoe.exceptions import NoMatchingDataError
from requests import HTTPError

from src.schemas import COUNTRIES, ColumnData
from warnings import warn
from datetime import time
import pandas as pd


def download_data_from_entsoe(
    data_name,
    table_columns,
    download_function,
    countries: str | list[str],
    start_date,
    end_date,
):
    if isinstance(countries, str):
        countries = [countries]
    total_data = []
    for country in countries:
        if country not in COUNTRIES:
            raise ValueError(f"Country {country} not found in COUNTRIES")
        country_code = COUNTRIES[country].code
        timezone = COUNTRIES[country].timezone
        start = pd.Timestamp(
            year=start_date.year,
            month=start_date.month,
            day=start_date.day,
            hour=0,
            minute=0,
            second=0,
            tz=timezone,
        )
        end = pd.Timestamp(
            year=end_date.year,
            month=end_date.month,
            day=end_date.day,
            hour=23,
            minute=59,
            second=59,
            tz=timezone,
        )

        retries = 0
        data_downloaded = False
        while retries < 3 and data_downloaded == False:
            try:
                data = download_function(country_code, start=start, end=end)

                data_downloaded = True
            except (HTTPError, NoMatchingDataError) as e:
                error = e
                retries += 1

                match error:
                    case NoMatchingDataError():
                        warn(
                            f"No matching {data_name}data for country {country} between {start_date} and {end_date}"
                        )

                    case HTTPError():
                        timeout = e.response.headers.get("Retry-After")
                        if timeout is not None:
                            time.sleep(int(timeout))
                        else:
                            time.sleep(10)

        if data_downloaded is False:
            warn(
                f"Could not download {data_name} data from entsoe between {start_date} and {end_date}, last error: "
                + str(error)
            )

        if isinstance(data, pd.Series):
            data = pd.DataFrame(
                data,
                columns=[col.name for col in table_columns if not col.primary_key],
            )
        # add country code to table
        data["country_code"] = country_code

        total_data.append(data)
    final_data = pd.concat(total_data)
    final_data["timestamp"] = final_data.index

    return final_data
