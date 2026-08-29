import numpy as np
import pandas as pd

from src.etl.read_data_from_oracle import _transform_generation_data


def test_generation_data_with_glitch_is_filled():
    data_with_glitch = pd.DataFrame({
        "TIMESTAMP" : ["2026-08-19 00:00", "2026-08-19 00:00", "2026-08-20 01:00", "2026-08-20 01:00", "2026-08-20 02:00", "2026-08-20 02:00"],
        "COUNTRY_CODE" : ["FR", "FR", "FR", "FR", "FR", "FR"],
        "GENERATION_SOURCE" : ["Solar", "Wind", "Solar", "Wind", "Solar", "Wind"],
        "GENERATION_TYPE" : ["Actual Aggregated", "Actual Aggregated", "Actual Aggregated", "Actual Aggregated", "Actual Aggregated", "Actual Aggregated"],
        "GENERATION" : [15000, 10000, 0, 0, 14000, 9000],
    }
    )
    data_with_glitch["TIMESTAMP"] = pd.to_datetime(data_with_glitch["TIMESTAMP"])
    pivoted_data = _transform_generation_data(data_with_glitch)

    assert np.isclose(pivoted_data["Solar"].iloc[1], (15000 + 14000) / 2)
    assert np.isclose(pivoted_data["Wind"].iloc[1], (10000+9000) / 2)


