# ETL for electricity data from Entso-e data

This data pipelines retrieves data from entso-e transparency platform, using entsoe-py library: https://github.com/EnergieID/entsoe-py.

## Data model

The data is stored in Oracle using separate tables for the main electricity-market
datasets and derived statistics.

| Table | Description |
|---|---|
| `load` | Electricity demand/load time series |
| `generation` | Generation by production type |
| `day_ahead_prices` | Day-ahead electricity prices |
| `prices_statistics` | Derived daily price statistics |
| `generation_statistics` | Derived generation statistics |

The tables stores timestamps and the bidding zone code for the request.

## Configuration

Create a `.env` file containing the following environment variables:

```text
ORACLE_PASSWORD
ORACLE_USER
ORACLE_WALLET_PASSWORD
ORACLE_DSN
ENTSOE_API_KEY
COUNTRY_CODE
WALLET_ENCRYPTING_PASSWORD
```

The Oracle wallet is stored locally as an encrypted file:

```text
data/wallet.zip.enc
```

The wallet is encrypted using Python's `cryptography` library.

> **Security:** credentials, API keys and wallet passwords should never be committed to the repository.

## Run the ETL locally

```bash
docker compose up --build uploader
```

By default, the uploader retrieves data from **three days ago through yesterday**.

The date range can be changed using the `START_DATE` and `END_DATE` environment variables.

### Linux / macOS

```bash
START_DATE=$(date -d "3 days ago" '+%Y-%m-%d') \
END_DATE=$(date -d "yesterday" '+%Y-%m-%d') \
docker compose up --build uploader
```

### Windows PowerShell

```powershell
$env:START_DATE = (Get-Date).AddDays(-3).ToString("yyyy-MM-dd")
$env:END_DATE = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")

docker compose up --build uploader
```

## Adding new countries
To get data for a specific bidding zone, add a new CountryData object to [schemas file](../schemas.py), indicating the specific entso-e code found at https://github.com/EnergieID/entsoe-py/blob/master/entsoe/mappings.py.