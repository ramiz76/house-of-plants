"""Selects and deletes data older than 24hrs from the short term database
and add this data to the longer term database"""

from os import environ
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
import psycopg2.extensions


def get_short_term_db_connection(config: dict) -> psycopg2.extensions.connection | None:
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


def retrieve_data_older_than_24_hours(connection: psycopg2.extensions.connection) -> None:
    """Retrieves data older than 24hrs from the short term RDS database and stores as a CSV file."""

    twenty_four_hours_ago = datetime.now() - timedelta(hours=6)
    formatted_time = twenty_four_hours_ago.strftime('%Y-%m-%d %H:%M:%S')

    query_for_data = f"""SELECT
        p.plant_name as plant_name,
        p.scientific_name as scientific_name,
        p.api_id as api_id,
        p.cycle as cycle,
        sr.last_watered as last_watered,
        sr.soil_moisture as soil_moisture,
        sr.temperature as temperature,
        p.sunlight as sunlight, 
        sr.recording_taken as recording_taken,
        o.longitude as longitude,
        o.latitude as latitude,
        o.country as country,
        o.continent as continent,
        b.name AS botanist_name,
        b.email as email,
        b.phone as phone,
        av.type_of_availability AS error
        FROM sensor_result sr
        JOIN plant p ON sr.plant_id = p.plant_id
        JOIN origin o ON p.origin_id = o.origin_id
        JOIN botanist b ON sr.botanist_id = b.botanist_id
        JOIN plant_availability av ON sr.availability_id = av.availability_id
        WHERE sr.recording_taken < '{formatted_time}'"""

    with connection.cursor() as cur:
        cur.execute(query_for_data)
        result = cur.fetchall()

    data = pd.DataFrame(result)
    data.to_csv("24_hour_data", index=False)


if __name__ == "__main__":

    load_dotenv()
    config = {
        "DATABASE_NAME": environ.get("DATABASE_NAME"),
        "DATABASE_USERNAME": environ.get("DATABASE_USERNAME"),
        "DATABASE_ENDPOINT": environ.get("DATABASE_ENDPOINT"),
        "DATABASE_PASSWORD": environ.get("DATABASE_PASSWORD")
    }

    short_db_conn = get_short_term_db_connection(config)

    retrieve_data_older_than_24_hours(short_db_conn)
