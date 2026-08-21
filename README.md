# Electricity Data Dashboard
This is a simple project to experiment with using oracle, github action and streamlit to built electricity data dashboards.

Electricity data for the previous day is automatically loaded to Oracle at 4 AM. The data comes from the entso-e API.

This is work in progress.

## Data upload on Oracle
This gets the data from the etso-e API and loads it to an Oracle database
- Put an ecrypted wallet in data, called `wallet.zip.enc`. It needs to be encrypted with python's cryttography library
- Set environment variables in .env file. The needed environment variables are:
    - ORACLE_PASSWORD: needed to access Oracle
    - ORACLE_USER
    - ORACLE_WALLET_PASSWORD
    - ORACLE_DSN
    - ENTSOE_API_KEY
    - COUNTRY_CODE: entso-e country code for which to download the data
    - WALLET_ENCRYPTING_PASSWORD: password used to encrypt the wallet

- You can now run ```docker compose up uploader --build``` to upload yesterday's data to Oracle
## Streamlit dashboard

```docker compose up dashboard```

And go to `http://localhost:8051` in the browser.
