from src.oracle_connection import create_oracle_connection

connection=create_oracle_connection()

cursor = connection.cursor()

cursor.execute("SELECT 'Hello Oracle' FROM dual")

print(cursor.fetchone())

connection.close()