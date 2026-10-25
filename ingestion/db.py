import os

import psycopg
from dbt.cli.params import host
from dotenv import load_dotenv

load_dotenv()

def connect()-> psycopg.Connection:
    return psycopg.connect(
        host = os.getenv("POSTGRES_HOST", "localhost"),
        port = os.getenv("POSTGRES_PORT", "5433"),
        dbname = os.getenv("POSTGRES_DB"),
        user = os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )