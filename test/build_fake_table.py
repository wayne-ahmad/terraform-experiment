import pyodbc
import agate
import agatesql
from dataquery_processor import _config

# Use this to generate the table script for fake data from the CSV. You may need to amend it
# manually, then import the data in a second step.

def generate_script(f, table_name):
    fake = agate.Table.from_csv(f)

    statement = fake.to_sql_create_statement(
        table_name,
        db_schema="dbo"
    )

    return statement



print(_config.conn)
query = generate_script("fake.csv", "fake")
print(query)

with pyodbc.connect(_config.conn) as conn:
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS dbo.fake")
    cursor.execute(query)
