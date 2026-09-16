from src.etl.tables import DayAheadPricesTable, GenerationTable, LoadTable

DOWNLOADABLE_TABLES = [LoadTable(), DayAheadPricesTable(), GenerationTable()]
