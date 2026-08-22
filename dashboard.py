import os

import streamlit as st

from src.dashboard.plots import create_plots
from src.etl.read_data_from_oracle import (
    get_and_trasform_data,
    get_available_countries,
    get_available_dates,
)
from src.oracle_connection import create_oracle_connection

st.set_page_config(layout="wide")

## set environment variables
os.environ["ORACLE_PASSWORD"] = st.secrets["ORACLE_PASSWORD"]
os.environ["ORACLE_USER"] = st.secrets["ORACLE_USER"]
os.environ["ORACLE_WALLET_PASSWORD"] = st.secrets["ORACLE_WALLET_PASSWORD"]
os.environ["ORACLE_DSN"] = st.secrets["ORACLE_DSN"]
os.environ["ENTSOE_API_KEY"] = st.secrets["ENTSOE_API_KEY"]
os.environ["WALLET_ENCRIPTING_PASSWORD"] = st.secrets["WALLET_ENCRIPTING_PASSWORD"]

connection = create_oracle_connection()
st.title("Electricity Data Dashboard")

#select country
available_countries = get_available_countries(connection, "load_raw")
selected_country = st.selectbox("Select a country", available_countries)
# select date
available_dates = get_available_dates(connection, "load_raw")
last_available_date = available_dates[-1]
selected_date = st.selectbox("Select a date", available_dates)

### get data from database + calculate statistics

load, day_ahead_prices, generation_pivot = get_and_trasform_data(connection, selected_date, selected_country)

load_figure, day_ahead_prices_figure, generation_figure = create_plots(
    load, day_ahead_prices, generation_pivot)

## show graphs
st.markdown(f"Data for {selected_date}, country : {os.environ['COUNTRY_CODE']}")

col1, col2 = st.columns([0.67, 0.33])
subcol1, subcol2 = col1.columns(2)

subcol1.subheader("Load")

subcol1.pyplot(load_figure)

subcol2.subheader("Day Ahead Prices")

subcol2.pyplot(day_ahead_prices_figure)

col1.subheader("Generation")

col1.pyplot(generation_figure, width='stretch')

##show statistics
col2.subheader("Price statistics")