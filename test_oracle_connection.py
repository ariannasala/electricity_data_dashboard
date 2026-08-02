import oracledb
import os

if os.path.exists("login_information.py"):
        from login_information import (
            DB_DSN,
            DB_PASSWORD,
            DB_USER,
            WALLET_LOCATION,
            WALLET_PASSWORD,
        )

        os.environ["WALLET_LOCATION"] = WALLET_LOCATION
        os.environ["DB_USER"] = DB_USER
        os.environ["DB_PASSWORD"] = DB_PASSWORD
        os.environ["DB_DSN"] = DB_DSN
        os.environ["WALLET_PASSWORD"] = WALLET_PASSWORD

connection=oracledb.connect(
     config_dir=os.environ["WALLET_LOCATION"],
     user=os.environ["DB_USER"],
     password=os.environ["DB_PASSWORD"],
     dsn=os.environ["DB_DSN"],
     wallet_location=os.environ["WALLET_LOCATION"],
     wallet_password=os.environ["WALLET_PASSWORD"])

cursor = connection.cursor()

cursor.execute("SELECT 'Hello Oracle' FROM dual")

print(cursor.fetchone())

connection.close()