"""Retrieves cleaned data from transform, and inserts into a Postgres db
This assumes the database already exists and has some initial data - see README / rds_schema.sql"""

from os import environ, remove

from dotenv import load_dotenv
import pandas as pd
import psycopg2
import psycopg2.extras
import psycopg2.extensions


def get_db_connection(config: dict) -> psycopg2.extensions.connection:
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
    # remove(file_name) - deletes file to clean up
    return plant_df


def insert_dataframe_into_origin_table(connection, dataframe: pd.DataFrame):
    """Inserts origin info from a dataframe into the postgres db"""

    with connection:
        with connection.cursor() as cur:

            cur.executemany(
                "INSERT INTO origin (longitude, latitude, country, continent) VALUES (%s, %s, %s, %s);", dataframe.values.tolist())
            connection.commit()


def insert_dataframe_into_botanist_table(connection, dataframe: pd.DataFrame):
    """Inserts botanist info from a dataframe into the postgres db"""

    with connection:
        with connection.cursor() as cur:

            cur.executemany(
                "INSERT INTO botanist (name, email, phone) VALUES (%s, %s, %s);", dataframe.values.tolist())
            connection.commit()


def add_origin_ids_to_plant_df(connection, total_dataframe: pd.DataFrame, plant_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Constructs list of origin ids based on plant data, 
    then given a plant dataframe, adds a new column with origin ids
    """

    origin_ids = []
    new_df = plant_dataframe

    with connection.cursor() as cur:
        new_df["origin_id"] = cur.execute(
            "SELECT origin_id FROM origin WHERE (longitude LIKE (%s) and latitude LIKE (%s));", (total_dataframe["longitude"], total_dataframe["latitude"]))

    return new_df


def insert_dataframe_into_plant_table(connection, dataframe: pd.DataFrame):
    """Inserts plant info from a dataframe into the postgres db"""
    with connection:
        with connection.cursor() as cur:

            cur.executemany("SELECT origin_id")
            cur.executemany(
                "INSERT INTO plant (plant_name, scientific_name, cycle, sunlight, api_id) VALUES (%s, %s, %s, %s, %s, %s);", dataframe.values.tolist())
            connection.commit()


if __name__ == "__main__":

    # try:
    load_dotenv()
    config = {
        "DATABASE_NAME": environ.get("DATABASE_NAME"),
        "DATABASE_USERNAME": environ.get("DATABASE_USERNAME"),
        "DATABASE_ENDPOINT": environ.get("DATABASE_ENDPOINT"),
        "DATABASE_PASSWORD": environ.get("DATABASE_PASSWORD")
    }

    conn = get_db_connection(config)

    full_df = create_dataframe()
    origin_df = full_df[["longitude", "latitude", "country", "continent"]]
    plant_df = full_df[["plant_name",
                        "scientific_name", "cycle", "sunlight"]]

    botanist_df = full_df[["botanist_name", "email", "phone"]]

    plant_df = add_origin_ids_to_plant_df(conn, full_df, plant_df)

    print(full_df.columns)

    print(origin_df.head())

    print(add_origin_ids_to_plant_df(conn, full_df, plant_df))
    # except:
    #     print("something went wrong")

    # finally:
    conn.close()
