import oracledb
import login_information as info

connection=oracledb.connect(
     config_dir=info.wallet_location,
     user=info.user,
     password=info.password,
     dsn=info.cs,
     wallet_location=info.wallet_location,
     wallet_password=info.wallet_password)

cursor = connection.cursor()

cursor.execute("SELECT 'Hello Oracle' FROM dual")

print(cursor.fetchone())

connection.close()