
from dataclasses import dataclass
from src.dashboard.plots import GENERATION_COLORS_PALETTE

@dataclass
class CountryData:
    code: str
    timezone: str

COUNTRIES = {
    "Spain" : CountryData("ES", "Europe/Madrid"),
    "France" : CountryData("FR", "Europe/Paris"),
    "Germany" : CountryData("DE_LU", "Europe/Berlin")
}

COUNTRY_CODES = {v.code: k for k, v in COUNTRIES.items()}

GENERATION_CATHEGORY_ORDER = list(GENERATION_COLORS_PALETTE.keys())
