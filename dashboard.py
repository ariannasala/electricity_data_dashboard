import os

import streamlit as st

from src.dashboard.plots import (
    create_generation_plot,
    create_load_plot,
    create_price_plot,
    create_treemap,
)
from src.etl.read_data_from_oracle import (
    get_available_countries,
    get_available_dates,
    get_data_for_dashboard,
    read_data_from_oracle,
    transform_generation_data,
)
from src.oracle_connection import create_oracle_connection
from src.schemas import COUNTRIES

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    hr {
        margin-top: 0 !important;
        margin-bottom: 0.1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.fragment
def show_price_statistics(statistics):
    ##show statistics
    prices_statistics_container = st.container(border=True)
    prices_statistics_container.subheader("Price statistics")

    if statistics is None or len(statistics) == 0:
        prices_statistics_container.write(
            "No statistics available for this date and country."
        )
        return

    statistics_to_show = statistics.round(2).T

    average_price = statistics_to_show.loc["AVERAGE", 0]
    maximum_price = statistics_to_show.loc["MAXIMUM", 0]
    minimum_price = statistics_to_show.loc["MINIMUM", 0]

    metric_column_1, metric_column_2, metric_column_3 = (
        prices_statistics_container.columns(3)
    )

    metric_column_1.metric(
        "Average [€/MWh]",
        f"{average_price:.1f}",
    )

    metric_column_2.metric(
        "Minimum [€/MWh]",
        f"{minimum_price:.1f}",
    )

    metric_column_3.metric(
        "Maximum [€/MWh]",
        f"{maximum_price:.1f}",
    )

    prices_statistics_container.markdown("#### Price spread")

    spread_column, value_column = prices_statistics_container.columns([2, 1])

    price_spread = spread_column.selectbox(
        "Select a price spread",
        ["Maximum and Minimum", "P99-P1", "P95-P5", "P90-P10"],
        label_visibility="collapsed",
    )

    match price_spread:
        case "Maximum and Minimum":
            spread = (
                statistics_to_show.loc["MAXIMUM", 0]
                - statistics_to_show.loc["MINIMUM", 0]
            )

        case "P99-P1":
            spread = statistics_to_show.loc["P99", 0] - statistics_to_show.loc["P01", 0]

        case "P95-P5":
            spread = statistics_to_show.loc["P95", 0] - statistics_to_show.loc["P05", 0]

        case "P90-P10":
            spread = statistics_to_show.loc["P90", 0] - statistics_to_show.loc["P10", 0]

    value_column.metric(
        "Spread [€/MWh]",
        f"{spread:.1f}",
    )

    prices_statistics_container.divider()

    negative_hours = statistics_to_show.loc["NUMBER_NEGATIVE_HOURS", 0]

    wind_capture_price = statistics_to_show.loc["WIND_CAPTURE_PRICE", 0]

    solar_capture_price = statistics_to_show.loc["SOLAR_CAPTURE_PRICE", 0]

    prices_statistics_container.metric(
        "Negative/zero-price hours",
        f"{negative_hours:.0f}",
    )

    new_metric_columns = prices_statistics_container.columns(2)
    new_metric_columns[0].metric(
        "Solar capture price [€/MWh]",
        f"{solar_capture_price:.1f}",
    )
    new_metric_columns[1].metric(
        "Wind capture price [€/MWh]",
        f"{wind_capture_price:.1f}",
    )


## set environment variables
os.environ["ORACLE_PASSWORD"] = st.secrets["ORACLE_PASSWORD"]
os.environ["ORACLE_USER"] = st.secrets["ORACLE_USER"]
os.environ["ORACLE_WALLET_PASSWORD"] = st.secrets["ORACLE_WALLET_PASSWORD"]
os.environ["ORACLE_DSN"] = st.secrets["ORACLE_DSN"]
os.environ["ENTSOE_API_KEY"] = st.secrets["ENTSOE_API_KEY"]
os.environ["WALLET_ENCRIPTING_PASSWORD"] = st.secrets["WALLET_ENCRIPTING_PASSWORD"]

connection = create_oracle_connection()
st.title("Electricity Data Dashboard")
st.write("Data Source: ENTSO-E Transparency Platform")

col1, col2 = st.columns(2)
# select country
available_country_codes = get_available_countries(connection, "load_raw")
available_countries = [
    country
    for country in COUNTRIES
    if COUNTRIES[country].code in available_country_codes
]
selected_country = col1.selectbox("Selected country:", available_countries)
selected_country_code = COUNTRIES[selected_country].code
# select date
available_dates = get_available_dates(connection, "load_raw")
last_available_date = available_dates[0]
selected_date = col2.date_input(
    "Selected date:",
    last_available_date,
    min_value=available_dates[-1],
    max_value=available_dates[0],
)

# get data
load, day_ahead_prices, generation = get_data_for_dashboard(
    connection, selected_date, selected_country_code
)
missing_data_load = load[load.isna().any(axis=1)]
missing_data_prices = day_ahead_prices[day_ahead_prices.isna().any(axis=1)]
generation_pivot = transform_generation_data(generation)
missing_data_generation = generation_pivot[generation_pivot.isna().any(axis=1)]

if len(missing_data_load) > 0:
    st.warning(f"{len(missing_data_load)} load data points are missing.")
if len(missing_data_prices) > 0:
    st.warning(f"{len(missing_data_prices)} day-ahead prices data points are missing.")
if len(missing_data_generation) > 0:
    st.warning(f"{len(missing_data_generation)} generation data points are missing.")

### plots + statistics from database


statistics = read_data_from_oracle(
    connection,
    "prices_statistics",
    selected_country_code,
    selected_date,
)

if (
    len(load) < 24
    or load is None
    or len(day_ahead_prices) < 24
    or day_ahead_prices is None
    or len(generation_pivot) < 24
    or generation_pivot is None
):
    st.error("No data available for this date. Please select another date.")
    st.stop()

load_figure = create_load_plot(load)
day_ahead_prices_figure = create_price_plot(day_ahead_prices)
generation_figure = create_generation_plot(generation_pivot)

## show graphs

load_column, price_column, price_statistics_column = st.columns([1, 1, 1])
with load_column:
    st.write("")
    load_container = st.container(gap="large")
    load_container.subheader("Electricity demand")
    load_container.plotly_chart(
        load_figure, width="stretch", config={"displayModeBar": False}
    )


with price_column:
    st.write("")
    price_container = st.container(gap="large")
    price_container.subheader("Day-ahead electricity prices")

    price_container.plotly_chart(
        day_ahead_prices_figure,
        width="stretch",
        config={"displayModeBar": False},
    )


with price_statistics_column:
    show_price_statistics(statistics)

generation_column, generation_statistics_column = st.columns([2, 1])
if "detailed_generation" not in st.session_state:
    st.session_state.detailed_generation = "Yes"


def update_generation_plot():
    global generation_figure
    generation_figure = create_generation_plot(
        generation_pivot, detailed=st.session_state.detailed_generation == "Yes"
    )


with generation_column:
    st.subheader("Generation")
    # detailed = st.radio(
    #    "Detailed view",
    #    ["Yes", "No"],
    #    horizontal=True,
    # )
    # if detailed != st.session_state.detailed_generation:
    #    st.session_state.detailed_generation = detailed
    #    update_generation_plot()
    st.plotly_chart(
        generation_figure,
        width="stretch",
        config={"displayModeBar": False},
    )

with generation_statistics_column:
    generation_statistics_container = st.container(border=True)
    generation_statistics_container.subheader("Daily Electricity Generation by Source")
    generation_statistics = read_data_from_oracle(
        connection,
        "generation_statistics",
        selected_country_code,
        selected_date,
    )
    if generation_statistics is None or len(generation_statistics) == 0:
        generation_statistics_container.write(
            "No generation statistics available for this date and country."
        )
    else:
        import matplotlib.pyplot as plt

        # TODO calculate separately actual consumption
        fig, ax = plt.subplots(figsize=(5, 5))
        fig = create_treemap(generation_statistics, generation_pivot)
        generation_statistics_container.plotly_chart(fig)
