import os
from src.oracle_connection import create_oracle_connection

if not os.environ.get("ENTSOE_API_KEY"):
    from streamlit import secrets
    os.environ["ORACLE_PASSWORD"] = secrets["ORACLE_PASSWORD"]
    os.environ["ORACLE_USER"] = secrets["ORACLE_USER"]
    os.environ["ORACLE_WALLET_PASSWORD"] = secrets["ORACLE_WALLET_PASSWORD"]
    os.environ["ORACLE_DSN"] = secrets["ORACLE_DSN"]
    os.environ["WALLET_ENCRIPTING_PASSWORD"] = secrets["WALLET_ENCRIPTING_PASSWORD"]

connection=create_oracle_connection()

cursor = connection.cursor()

cursor.execute("SELECT 'Hello Oracle' FROM dual")

print(cursor.fetchone())

connection.close()