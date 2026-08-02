import os

import pandas as pd
from datetime import date, timedelta

def read_yesterday_data(connection, table_name, yesterday):
    sql = f"""
    SELECT * FROM {table_name}
    WHERE timestamp >= TIMESTAMP '{yesterday} 00:00:00'
    AND timestamp < TIMESTAMP '{yesterday} 23:59:59'
    """

    df = pd.read_sql(sql, connection)

    return df

def create_plots(load, day_ahead_prices, generation):
    import matplotlib.pyplot as plt

    load_figure, load_ax = plt.subplots()

    load.plot(x="TIMESTAMP", y="LOAD", kind="line", ax=load_ax)

    day_ahead_prices_figure, day_ahead_prices_ax = plt.subplots()

    day_ahead_prices.plot(x="TIMESTAMP", y="DAY_AHEAD_PRICES", kind="line", ax = day_ahead_prices_ax)

    generation_figure, generation_ax = plt.subplots()
    generation.plot.area(x="TIMESTAMP", ax = generation_ax)
    plt.show()


    return load_figure, day_ahead_prices_figure, generation_figure


def create_dashboard(yesterday, load_figure, day_ahead_prices_figure, generation_figure):
    import streamlit as st



    country = load["COUNTRY_CODE"].iloc[0]

    st.title("Electricity Data Dashboard")
    st.markdown(f"Data for yesterday {yesterday}, country : {country}")


    st.subheader("Load")
    
    st.pyplot(load_figure)

    st.subheader("Day Ahead Prices")
    
    st.pyplot(day_ahead_prices_figure)

    st.subheader("Generation")
    
    st.pyplot(generation_figure)



    

if __name__ == "__main__":
    import oracledb

    if os.path.exists("login_information.py"):
        from login_information import (
            DB_DSN,
            DB_PASSWORD,
            DB_USER,
            WALLET_LOCATION,
            WALLET_PASSWORD,
        )

        os.environ["WALLET_LOCATION"] = WALLET_LOCATION
        os.environ["DB_USER"] = DB_USER
        os.environ["DB_PASSWORD"] = DB_PASSWORD
        os.environ["DB_DSN"] = DB_DSN
        os.environ["WALLET_PASSWORD"] = WALLET_PASSWORD

    connection=oracledb.connect(
         config_dir=os.environ["WALLET_LOCATION"],
         user=os.environ["DB_USER"],
         password=os.environ["DB_PASSWORD"],
         dsn=os.environ["DB_DSN"],
         wallet_location=os.environ["WALLET_LOCATION"],
         wallet_password=os.environ["WALLET_PASSWORD"])
    
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    load = read_yesterday_data(connection, "load_raw", yesterday)
    day_ahead_prices = read_yesterday_data(connection, "day_ahead_prices_raw", yesterday)
    generation = read_yesterday_data(connection, "generation_raw", yesterday)

    load_figure, day_ahead_prices_figure, generation_figure = create_plots(load, day_ahead_prices, generation)

    #create_dashboard(yesterday, load_figure, day_ahead_prices_figure, generation_figure)

    