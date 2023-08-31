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


def retrieve_data_older_than_24_hours(conn):

    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

    query_for_data = f"""SELECT
        p.plant_name,
        p.scientific_name,
        p.api_id,
        p.cycle,
        sr.last_watered,
        sr.soil_moisture,
        sr.temperature,
        p.sunlight, 
        sr.recording_taken,
        o.longitude,
        o.latitude,
        o.country,
        o.continent,
        b.name AS botanist_name,
        b.email,
        b.phone,
        av.type_of_availability AS error
        FROM sensor_result sr
        JOIN plant p ON sr.plant_id = p.plant_id
        JOIN origin o ON p.origin_id = o.origin_id
        JOIN botanist b ON sr.botanist_id = b.botanist_id
        JOIN plant_availability av ON sr.availability_id = av.availability_id
        WHERE sr.recording_taken < {twenty_four_hours_ago}"""


def combine_csv_files():

    main_csv_dateframe = pd.read_csv('original_data/plant_data.csv')
    new_csv_dateframe = pd.read_csv('24hr_data/plant_data1.csv')

    combined_df = pd.concat(
        [main_csv_dateframe, new_csv_dateframe], ignore_index=True)

    combined_df = combined_df.drop(columns=['Unnamed: 0'])

    combined_df.to_csv('combined.csv', index=False)


if __name__ == "__main__":

    load_dotenv()
    config = {
        "DATABASE_NAME": environ.get("DATABASE_NAME"),
        "DATABASE_USERNAME": environ.get("DATABASE_USERNAME"),
        "DATABASE_ENDPOINT": environ.get("DATABASE_ENDPOINT"),
        "DATABASE_PASSWORD": environ.get("DATABASE_PASSWORD")
    }

    short_db_conn = get_short_term_db_connection(config)
