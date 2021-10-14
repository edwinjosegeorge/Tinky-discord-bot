import os
import psycopg2
import urllib.parse as urlparse
import pandas as pd
from dotenv import load_dotenv

# read database connection url from the enivron variable we just set.
load_dotenv()
url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port


def load_data(conn):
    data = pd.read_excel('GCEKList.xlsx', sheet_name="CS")

    for index, row in data.iterrows():
        name = row["Name"]
        admn = row["Addmission"]
        branch = str(row["Class"])[:2].strip()
        year = str(row["Class"])[2:].strip()
        conn.execute(f"INSERT INTO gcek_list (name, admn, branch, year) \
        VALUES ('{name}', '{admn}', '{branch}', '{year}')")
        print(f"added {name}")


con = None
try:
    # create a new database connection by calling the connect() function
    con = psycopg2.connect(dbname=dbname, user=user,
                           password=password, host=host, port=port)

    #  create a new cursor
    cur = con.cursor()

    load_data(cur)

    # close the communication with the HerokuPostgres
    con.commit()
    cur.close()
except Exception as error:
    print('Cause: {}'.format(error))

finally:
    # close the communication with the database server by calling the close()
    if con is not None:
        con.close()
        print('Database connection closed.')
