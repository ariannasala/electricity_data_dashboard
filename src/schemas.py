
from dataclasses import dataclass

@dataclass
class CountryData:
    code: str
    timezone: str

COUNTRIES = {
    "Spain" : CountryData("ES", "Europe/Madrid"),
    "France" : CountryData("FR", "Europe/Paris"),
    "Germany" : CountryData("DE", "Europe/Berlin")
}

COUNTRY_CODES = {v.code: k for k, v in COUNTRIES.items()}