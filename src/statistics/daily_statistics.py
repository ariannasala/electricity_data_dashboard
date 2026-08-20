import pandas as pd

def calculate_price_statistics(prices, generation_data, country_code):

    zone_prices = prices[prices["country_code"] == country_code]
    maximum_price = zone_prices["day_ahead_price"].max()
    minimum_price = zone_prices["day_ahead_price"].min()
    maximum_price_hour = zone_prices[zone_prices["day_ahead_price"] == maximum_price]["hour"].values[0]
    minimum_price_hour = zone_prices[zone_prices["day_ahead_price"] == minimum_price]["hour"].values[0]
    p90 = zone_prices["day_ahead_price"].quantile(0.90)
    p10 = zone_prices["day_ahead_price"].quantile(0.10)
    p95 = zone_prices["day_ahead_price"].quantile(0.95)
    p99 = zone_prices["day_ahead_price"].quantile(0.99)
    p01 = zone_prices["day_ahead_price"].quantile(0.01)
    number_negative_hours = len(zone_prices[zone_prices["day_ahead_price"] <= 0])

    generation_zone = generation_data[generation_data["country_code"] == country_code]
    solar_generation = generation_zone[generation_zone["generation_source"] == "Solar"]
    solar_generation_price = pd.merge(solar_generation, zone_prices, on = "timestamp", how = "inner")
    solar_capture_price = sum(solar_generation_price["day_ahead_price"] * solar_generation_price["generation"]) / sum(solar_generation_price["generation"])

    wind_generation = generation_zone[(generation_zone["generation_source"] == "Wind Onshore") | (generation_zone["generation_source"] == "Wind Offshore")]
    wind_generation_price = pd.merge(wind_generation, zone_prices, on = "timestamp", how = "inner")
    wind_capture_price = sum(wind_generation_price["day_ahead_price"] * wind_generation_price["generation"]) / sum(wind_generation_price["generation"])

    return pd.Series(
        {
            "country_code": country_code,
            "maximum_price": maximum_price,
            "minimum_price": minimum_price,
            "maximum_price_hour": maximum_price_hour,
            "minimum_price_hour": minimum_price_hour,
            "p90": p90,
            "p10": p10,
            "p95": p95,
            "p99": p99,
            "p01": p01,
            "number_negative_hours": number_negative_hours,
            "solar_capture_price": solar_capture_price,
            "wind_capture_price": wind_capture_price
        }
    )