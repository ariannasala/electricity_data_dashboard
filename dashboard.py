import os

import streamlit as st

from src.dashboard.dashboard import create_plots
from src.etl.read_data_from_oracle import get_available_dates, read_data_from_oracle
from src.oracle_connection import create_oracle_connection

connection = create_oracle_connection()

available_dates = get_available_dates(connection, "load_raw")
last_available_date = available_dates[-1]

selected_date = st.selectbox("Select a date", available_dates)

load = read_data_from_oracle(connection, "load_raw", selected_date)
day_ahead_prices = read_data_from_oracle(
    connection, "day_ahead_prices_raw", selected_date
)
generation = read_data_from_oracle(
    connection, 
    "generation_raw", 
    selected_date)

generation["SOURCE"] = generation["GENERATION_TYPE"] + " " + generation["GENERATION_SOURCE"]

generation_pivot = generation.pivot(index="TIMESTAMP", columns="SOURCE", values="GENERATION").reset_index()


st.write(generation_pivot)
load_figure, day_ahead_prices_figure, generation_figure = create_plots(
    load, day_ahead_prices, generation_pivot
)

st.title("Electricity Data Dashboard")
st.markdown(f"Data for {selected_date}, country : {os.environ['COUNTRY_CODE']}")

st.subheader("Load")

st.pyplot(load_figure)

st.subheader("Day Ahead Prices")

st.pyplot(day_ahead_prices_figure)

st.subheader("Generation")

st.pyplot(generation_figure)