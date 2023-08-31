"""Retrieves cleaned data from transform, and inserts into a Postgres db
This assumes the database already exists and has some initial data - see README / rds_schema.sql"""

import os

from dotenv import load_dotenv
import numpy as np
import pandas as pd
import psycopg2
import psycopg2.errors
import psycopg2.extras
import psycopg2.extensions


def get_db_connection(config: dict) -> psycopg2.extensions.connection | None:
    """
    Attempts to connect to a postgres database using psycopg2
    returning a connection object if successful
    """

    try:
        return psycopg2.connect(dbname=config["DATABASE_NAME"],
                                user=config["DATABASE_USERNAME"],
                                host=config["DATABASE_ENDPOINT"],
                                password=config["DATABASE_PASSWORD"],
                                cursor_factory=psycopg2.extras.RealDictCursor)

    except:
        raise psycopg2.DatabaseError("Error connecting to database.")


def create_dataframe(file_name: str = "data/plant_data.csv") -> pd.DataFrame:
    """Returns the data from a file in a dataframe. Takes filename, or defaults to plant_data.csv"""

    plant_df = pd.read_csv(file_name)
    os.remove(file_name)
    return plant_df


def insert_dataframe_into_origin_table(connection: psycopg2.extensions.connection, dataframe: pd.DataFrame) -> None:
    """Inserts origin info from a dataframe into the postgres db"""

    for index, row in dataframe.iterrows():
        try:
            with connection:
                with connection.cursor() as cur:
                    cur.execute(
                        "INSERT INTO origin (longitude, latitude, country, continent) VALUES (%s, %s, %s, %s);", row.to_list())
                    connection.commit()

        except psycopg2.errors.UniqueViolation as e:
            continue  # We don't want duplicate values, but also don't want to crash
        except:
            print("Unexpected Error Ocurred")
            print(e.args)
            print(str(e))


def insert_dataframe_into_botanist_table(connection: psycopg2.extensions.connection, dataframe: pd.DataFrame) -> None:
    """Inserts botanist info from a dataframe into the postgres db"""

    for index, row in dataframe.iterrows():
        try:
            with connection:
                with connection.cursor() as cur:
                    cur.execute(
                        "INSERT INTO botanist (name, email, phone) VALUES (%s, %s, %s);", row.to_list())
                    connection.commit()

        except psycopg2.errors.UniqueViolation as e:
            continue  # We don't want duplicate values, but also don't want to crash
        except:
            print("Unexpected Error Ocurred")
            print(e.args)
            print(str(e))


def add_origin_ids_to_plant_df(connection: psycopg2.extensions.connection, total_dataframe: pd.DataFrame, plant_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs list of origin ids based on plant data, 
    then given a plant dataframe, adds a new column with origin ids
    """

    plant_dataframe = plant_dataframe.copy()
    origin_ids = []

    for index, row in total_dataframe.iterrows():
        with connection.cursor() as cur:
            cur.execute(
                "SELECT origin_id FROM origin WHERE (longitude = (%s) and latitude = (%s));", (row["longitude"], row["latitude"]))
            current_origin_id = cur.fetchone()
        origin_ids.append(current_origin_id["origin_id"])

    plant_dataframe["origin_id"] = origin_ids
    return plant_dataframe


def insert_dataframe_into_plant_table(connection: psycopg2.extensions.connection, dataframe: pd.DataFrame) -> None:
    """Inserts plant info from a dataframe into the postgres db"""

    for index, row in dataframe.iterrows():
        try:
            with connection:
                with connection.cursor() as cur:
                    cur.execute(
                        "INSERT INTO plant (plant_name, scientific_name, cycle, sunlight, api_id, origin_id) VALUES (%s, %s, %s, %s, %s, %s);", row.to_list())
                    connection.commit()

        except psycopg2.errors.UniqueViolation as e:
            continue  # We don't want duplicate values, but also don't want to crash
        except:
            print("Unexpected Error Ocurred")
            print(e.args)
            print(str(e))


def insert_dataframe_into_sensor_result_table(connection: psycopg2.extensions.connection, dataframe: pd.DataFrame) -> None:
    """
    Finally inserts sensor info from a dataframe into the postgres db. 
    relies on all other data already having been inserted
    """

    for index, row in dataframe.iterrows():
        with connection:
            with connection.cursor() as cur:
                cur.execute(
                    "INSERT INTO sensor_result (last_watered, soil_moisture, temperature, recording_taken, availability_id, botanist_id, plant_id) VALUES (%s, %s, %s, %s, %s, %s, %s);", row.to_list())
                connection.commit()


def add_availability_ids_to_sensor_df(connection: psycopg2.extensions.connection, total_dataframe: pd.DataFrame, sensor_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs list of availability ids based on sensor data, 
    then given a sensor dataframe, adds a new column with availability ids
    """

    sensor_dataframe = sensor_dataframe.copy()
    availability_ids = []

    for index, row in total_dataframe.iterrows():
        with connection.cursor() as cur:
            cur.execute(
                "SELECT availability_id FROM plant_availability WHERE type_of_availability LIKE %s;", (str(row["error"]),))
            current_availability_id = cur.fetchone()

        if current_availability_id is None:
            availability_ids.append(1)
        else:
            availability_ids.append(
                current_availability_id["availability_id"])

    sensor_dataframe["availability_id"] = availability_ids
    return sensor_dataframe


def add_botanist_ids_to_sensor_df(connection: psycopg2.extensions.connection, total_dataframe: pd.DataFrame, sensor_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs list of botanist ids based on sensor data, 
    then given a sensor dataframe, adds a new column with botanist ids
    """

    sensor_dataframe = sensor_dataframe.copy()
    botanist_ids = []

    for index, row in total_dataframe.iterrows():
        with connection.cursor() as cur:
            cur.execute(
                "SELECT botanist_id FROM botanist WHERE phone LIKE %s;", (str(row["phone"]),))
            current_botanist_id = cur.fetchone()

        if current_botanist_id is None:
            botanist_ids.append(None)
        else:
            botanist_ids.append(current_botanist_id["botanist_id"])

    sensor_dataframe["botanist_id"] = botanist_ids
    return sensor_dataframe


def add_plant_ids_to_sensor_df(connection: psycopg2.extensions.connection, total_dataframe: pd.DataFrame, sensor_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs list of plant ids based on sensor data, 
    then given a sensor dataframe, adds a new column with plant ids
    """

    sensor_dataframe = sensor_dataframe.copy()
    plant_ids = []

    for index, row in total_dataframe.iterrows():
        with connection.cursor() as cur:
            cur.execute(
                "SELECT plant_id FROM plant WHERE api_id = %s;", (row["api_id"],))
            current_plant_id = cur.fetchone()

        if current_plant_id is None:
            plant_ids.append(None)
        else:
            plant_ids.append(current_plant_id["plant_id"])

    sensor_dataframe["plant_id"] = plant_ids
    return sensor_dataframe


def load_all_data(connection: psycopg2.extensions.connection) -> None:
    """Given a db connection and csv file, inserts all data into the database"""
    # get all data
    full_df = create_dataframe()

    # split into individual dfs for insertion
    origin_df = full_df[["longitude", "latitude", "country", "continent"]]
    plant_df = full_df[["plant_name",
                        "scientific_name", "cycle", "sunlight", "api_id"]]
    botanist_df = full_df[["botanist_name", "email", "phone"]]
    sensor_df = full_df[['last_watered', 'soil_moisture',
                         'temperature', 'recording_taken']]

    # insert data with no foreign key requirements
    insert_dataframe_into_origin_table(connection, origin_df)
    insert_dataframe_into_botanist_table(connection, botanist_df)

    # update plant data with origin keys
    plant_df = add_origin_ids_to_plant_df(connection, full_df, plant_df)

    insert_dataframe_into_plant_table(connection, plant_df)

    # update sensor data with avail, botanist and plant ids.
    sensor_df = add_availability_ids_to_sensor_df(
        connection, full_df, sensor_df)
    sensor_df = add_botanist_ids_to_sensor_df(connection, full_df, sensor_df)
    sensor_df = add_plant_ids_to_sensor_df(connection, full_df, sensor_df)

    # sensor_df = sensor_df.where(pd.notnull(sensor_df), None)

    sensor_df = sensor_df.replace(np.nan, None)

    insert_dataframe_into_sensor_result_table(connection, sensor_df)


if __name__ == "__main__":

    load_dotenv()
    config = {
        "DATABASE_NAME": os.environ.get("DATABASE_NAME"),
        "DATABASE_USERNAME": os.environ.get("DATABASE_USERNAME"),
        "DATABASE_ENDPOINT": os.environ.get("DATABASE_ENDPOINT"),
        "DATABASE_PASSWORD": os.environ.get("DATABASE_PASSWORD")
    }

    conn = get_db_connection(config)

    load_all_data(conn)

    conn.close()
