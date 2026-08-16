# Electricity Data Dashboard
This is a simple project to experiment with using oracle, github action and streamlit to built electricity data dashboards.

Electricity data for the previous day is automatically loaded to Oracle at 4 AM. The data comes from the entso-e API.

This is work in progress.

## Data upload on Oracle
This gets the data from the etso-e API and loads it to an Oracle database
- Put an encripted oracle wallet in the ```data``` folder
- Set environment variables in .env file. The needed environment variables are:
    - ORACLE_PASSWORD: needed to access Oracle
    - ORACLE_USER
    - ORACLE_WALLET_PASSWORD
    - ORACLE_DSN
    - ENTSOE_API_KEY
    - COUNTRY_CODE: entso-e country code for which to 

- Do ```docker compose build --build-arg ENCRIPTING_PASSWORD=<encripting_password_for_the_wallet>```
- You can now run ```docker compose up``` to upload yesterday's data to Oracle