import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()

def get_db_connection():
    url = os.getenv("DATABASE_URL")
    password = os.getenv("DATABASE_PASSWORD")

    if not url or not password:
        raise RuntimeError(
            "DATABASE_URL and DATABASE_PASSWORD must be configured."
        )

    return psycopg.connect(
        url,
        password=password,
        sslmode="require",
        connect_timeout=10,
        prepare_threshold=None,
        row_factory=dict_row
    )