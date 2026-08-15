import oracledb
import os


connection=oracledb.connect(
     config_dir=os.environ["WALLET_LOCATION"],
     user=os.environ["ORACLE_USER"],
     password=os.environ["ORACLE_PASSWORD"],
     dsn=os.environ["ORACLE_DSN"],
     wallet_location=os.environ["WALLET_LOCATION"],
     wallet_password=os.environ["ORACLE_WALLET_PASSWORD"])

cursor = connection.cursor()

cursor.execute("SELECT 'Hello Oracle' FROM dual")

print(cursor.fetchone())

connection.close()