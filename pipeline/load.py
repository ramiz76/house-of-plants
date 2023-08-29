"""Retrieves cleaned data from transform, and inserts into a Postgres db
This assumes the database already exists and has some initial data - see README / rds_schema.sql"""

from dotenv import load_dotenv
import os

import pandas as pd
import psycopg2


def get_db_connection(config: dict) -> psycopg2.connection:
    """Attempts to connect to a postgres database using psycopg2
    returning a connection object if successful"""

    try:
        return psycopg2.connect(dbname=config["DATABASE_NAME"],
                                user=config["DATABASE_USERNAME"],
                                host=config["DATABASE_ENDPOINT"],
                                password=config["DATABASE_PASSWORD"],
                                cursor_factory=psycopg2.extras.RealDictCursor)

    except:
        raise psycopg2.DatabaseError("Error connecting to database.")


def create_dataframe(file_name: str = "plant_data.csv") -> pd.DataFrame:
    """Returns the data from a file in a dataframe. Takes filename, or defaults to plant_data.csv"""

    plant_df = pd.read_csv(file_name)
    return plant_df


def insert_dataframe_into_database(dataframe: pd.DataFrame, connection: psycopg2.connection):
    """Inserts the whole datarame into a postgres database"""

    with connection.cursor as cur:
        cur.executemany("SQL GOES HERE", dataframe.values.tolist())


if __name__ == "__main__":

    load_dotenv()
    config = {
        "DATABASE_NAME": os.environ.get("DATABASE_NAME"),
        "DATABASE_USERNAME": os.environ.get("DATABASE_USERNAME"),
        "DATABASE_ENDPOINT": os.environ.get("DATABASE_ENDPOINT"),
        "DATABASE_PASSWORD": os.environ.get("DATABASE_PASSWORD"),

    }

    conn = get_db_connection(config)

    plant_df = create_dataframe()

    insert_dataframe_into_database(plant_df, conn)

    conn.close()
