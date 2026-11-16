import os
import pandas as pd
from sqlalchemy import create_engine, URL
from dotenv import load_dotenv
load_dotenv()

DB_PASSWORD = os.getenv("MYSQL_PASSWORD")

if not DB_PASSWORD:
    raise RuntimeError(
        "MYSQL_PASSWORD environment variable is not set. "
        "Please configure it before running the dashboard."
    )

connection_url = URL.create(
    drivername="mysql+pymysql",
    username="neha",
    password=DB_PASSWORD,
    host="localhost",
    port=3306,
    database="horizon_hospitality_full",
)

engine = create_engine(connection_url)


def fetch_data(query):
    with engine.connect() as connection:
        return pd.read_sql(query, connection)
