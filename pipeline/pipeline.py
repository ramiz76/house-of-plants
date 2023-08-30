"""Pipeline script that combines all the extract, transform and load scripts"""

from os import environ, remove
from dotenv import load_dotenv

from load_short_term import get_db_connection, load_all_data
from extract import extract_and_create_csv
from transform import transform_script


if __name__ == "__main__":

    extract_and_create_csv()
    transform_script()

    load_dotenv()
    config = {
        "DATABASE_NAME": environ.get("DATABASE_NAME"),
        "DATABASE_USERNAME": environ.get("DATABASE_USERNAME"),
        "DATABASE_ENDPOINT": environ.get("DATABASE_ENDPOINT"),
        "DATABASE_PASSWORD": environ.get("DATABASE_PASSWORD")
    }

    conn = get_db_connection(config)

    load_all_data(conn)

    conn.close()
