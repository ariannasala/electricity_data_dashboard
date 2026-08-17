def create_plots(load, day_ahead_prices, generation):
    import matplotlib.pyplot as plt

    load_figure, load_ax = plt.subplots()

    load.plot(x="TIMESTAMP", y="LOAD", kind="line", ax=load_ax)

    day_ahead_prices_figure, day_ahead_prices_ax = plt.subplots()

    day_ahead_prices.plot(
        x="TIMESTAMP", y="DAY_AHEAD_PRICES", kind="line", ax=day_ahead_prices_ax
    )

    generation_figure, generation_ax = plt.subplots(figsize=(20, 10))
    generation.plot.area(x="TIMESTAMP", ax=generation_ax)
    plt.tight_layout()


    return load_figure, day_ahead_prices_figure, generation_figure