import plotly.express as px
import plotly.graph_objects as go


GENERATION_COLORS_PALETTE = {
    "wind": px.colors.sequential.Greens,
    "solar": px.colors.sequential.YlOrBr,
    "storage": px.colors.sequential.Purp,
    "coal": px.colors.sequential.Greys,
    "hydro": px.colors.sequential.Blues,
    "gas": px.colors.sequential.solar,
    "nuclear": px.colors.sequential.Agsunset,
    "biomass": px.colors.sequential.Purples,
    "oil": px.colors.sequential.Oranges,
    "other": px.colors.sequential.amp,
}
def create_plots(load, day_ahead_prices, generation):

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    load_figure = px.line(
        load,
        x="TIMESTAMP",
        y="LOAD",
        labels={
            "TIMESTAMP": "",
            "LOAD": "Load [MW]",
        },
    )

    load_figure.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="x unified",
        legend_title_text="",
    )

    # ------------------------------------------------------------------
    # Day-ahead prices
    # ------------------------------------------------------------------

    day_ahead_prices_figure = px.line(
        day_ahead_prices,
        x="TIMESTAMP",
        y="DAY_AHEAD_PRICES",
        labels={
            "TIMESTAMP": "",
            "DAY_AHEAD_PRICES": "Price [€/MWh]",
        },
    )

    day_ahead_prices_figure.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="x unified",
        legend_title_text="",
    )

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    generation_columns = [
        column
        for column in generation.columns
        if column != "TIMESTAMP"
    ]

    generation_category_order = [
        "wind",
        "solar",
        "hydro",
        "nuclear",
        "gas",
        "coal",
        "biomass",
        "oil",
        "other",
    ]

    def get_generation_category(generation_type):
        generation_type_lower = generation_type.lower()

        for category in generation_category_order:
            if category in generation_type_lower:
                return category

        return "other"

    def make_transparent_color(color, opacity=0.5):
        rgb_values = color.replace("rgb(", "").replace(")", "").split(",")
        red, green, blue = [int(value) for value in rgb_values]

        return f"rgba({red}, {green}, {blue}, {opacity})"

    generation_categories = {
        generation_column: get_generation_category(generation_column)
        for generation_column in generation_columns
    }

    generation_color_map = {}

    for category, palette in GENERATION_COLORS_PALETTE.items():
        category_columns = [
            column
            for column in generation_columns
            if generation_categories[column] == category
        ]

        number_of_columns = len(category_columns)

        if number_of_columns == 0:
            continue

        # Avoid the very lightest colors in sequential palettes.
        palette_colors = palette[2:]

        if number_of_columns == 1:
            selected_colors = [
                palette_colors[0]
            ]
        else:
            color_indices = [
                round(
                    index
                    * (len(palette_colors) - 1)
                    / (number_of_columns - 1)
                )
                for index in range(number_of_columns)
            ]

            selected_colors = [
                palette_colors[index]
                for index in color_indices
            ]

        for generation_column, generation_color in zip(
            category_columns,
            selected_colors,
        ):
            generation_color_map[generation_column] = generation_color

    generation_figure = go.Figure()

    positive_generation_columns = [
        column
        for column in generation_columns
        if "Actual Consumption" not in column
    ]

    negative_generation_columns = [
        column
        for column in generation_columns
        if "Actual Consumption" in column
    ]
    # Negative consumption
    for generation_column in negative_generation_columns:
        generation_figure.add_trace(
            go.Scatter(
                x=generation["TIMESTAMP"],
                y=generation[generation_column],
                name=generation_column,
                mode="lines",
                stackgroup="consumption",
                line=dict(
                    color=generation_color_map[generation_column],
                    width=1.5,
                ),
                fillcolor=generation_color_map[generation_column],
                hovertemplate=(
                    f"<b>{generation_column}</b><br>"
                    "%{y:,.0f} MW"
                    "<extra></extra>"
                ),
                opacity=0.5
            )
        )

    # Positive generation
    for generation_column in positive_generation_columns:
        line_color = generation_color_map[generation_column]

        generation_figure.add_trace(
            go.Scatter(
                x=generation["TIMESTAMP"],
                y=generation[generation_column],
                name=generation_column,
                mode="lines",
                stackgroup="generation",
                line=dict(
                    color=line_color,
                    width=1.5,
                ),
                fillcolor=make_transparent_color(
                    line_color
                ),
                hovertemplate=(
                    f"<b>{generation_column}</b><br>"
                    "%{y:,.0f} MW"
                    "<extra></extra>"
                ),
                opacity=0.5
            )
        )

    generation_figure.update_layout(
    height=700,
    margin=dict(l=10, r=10, t=10, b=10),
    hovermode="x unified",
    hoverlabel=dict(
        font_size=12,
    ),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.15,
        xanchor="center",
        x=0.5,
    ),
    )
    generation_figure.update_yaxes(
    showgrid=True,
    gridcolor="rgba(128, 128, 128, 0.3)",
    gridwidth=1,
    griddash="dot",
    layer="above traces",
)

    return (
        load_figure,
        day_ahead_prices_figure,
        generation_figure,
    )