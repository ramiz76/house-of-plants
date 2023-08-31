"""Selects and deletes data older than 24hrs from the short term database
and add this data to the longer term database"""

import os
from os import environ
from datetime import datetime, timedelta

from boto3 import client
from botocore.client import BaseClient
import pandas as pd
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
import psycopg2.extensions

COLUMNS = ['plant_name', 'scientific_name', 'api_id', 'cycle', 'last_watered', 'soil_moisture',
           'temperature', 'sunlight', 'recording_taken', 'longitude', 'latitude', 'country',
           'continent', 'botanist_name', 'email', 'phone', 'error']


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
    """Retrieves data older than 24hrs from the short term RDS database and stores as a CSV file
    and deletes data older than 24hrs from the RDS."""

    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    formatted_time = twenty_four_hours_ago.strftime("%Y-%m-%d %H:%M:%S")
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
        cur.execute(
            f"DELETE FROM sensor_result sr WHERE sr.recording_taken < '{formatted_time}'")

    data = pd.DataFrame(result, columns=COLUMNS)
    data.to_csv("long_term_data/24_hour_data.csv", index=False)


def create_download_folders() -> None:
    """Creates a folder with the name 'long_term_data' if it doesn't already exist."""

    folder_exists = os.path.exists("long_term_data")

    if not folder_exists:
        os.makedirs("long_term_data")


def download_data_from_s3(current_s3: BaseClient) -> None:
    """Downloads the csv file containing the older than 24hrs data. If no such file is found,
    an empty file is created"""

    download_path = os.path.join(
        "long_term_data", os.path.basename("full_s3_data.csv"))

    try:
        current_s3.download_file(environ.get(
            "BUCKET_NAME"), "long_term_data/full_s3_data.csv", download_path)

    except:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv("long_term_data/full_s3_data.csv", index=False)


def combine_csv_files() -> None:
    """Combines the new 24 hour old data with the existing file containing all old data"""

    main_csv_dateframe = pd.read_csv("long_term_data/full_s3_data.csv")
    new_csv_dateframe = pd.read_csv("long_term_data/24_hour_data.csv")

    combined_df = pd.concat(
        [main_csv_dateframe, new_csv_dateframe], ignore_index=True)

    os.remove("long_term_data/full_s3_data.csv")
    os.remove("long_term_data/24_hour_data.csv")

    combined_df.to_csv('long_term_data/full_s3_data.csv', index=False)


def upload_files_to_s3(current_s3: BaseClient) -> None:
    """Uploads the new combined csv file with all data older than 24hrs,
    replacing file that exists in the s3 bucket."""

    current_s3.upload_file("long_term_data/full_s3_data.csv", environ.get(
        "BUCKET_NAME"), "full_s3_data.csv")


if __name__ == "__main__":

    load_dotenv()

    config = {
        "DATABASE_NAME": environ.get("DATABASE_NAME"),
        "DATABASE_USERNAME": environ.get("DATABASE_USERNAME"),
        "DATABASE_ENDPOINT": environ.get("DATABASE_ENDPOINT"),
        "DATABASE_PASSWORD": environ.get("DATABASE_PASSWORD")
    }

    short_db_conn = get_short_term_db_connection(config)

    create_download_folders()
    retrieve_data_older_than_24_hours(short_db_conn)
    current_s3 = client("s3", aws_access_key_id=environ.get("ACCESS_KEY_ID"),
                        aws_secret_access_key=environ.get("SECRET_ACCESS_KEY"))
    download_data_from_s3(current_s3)
    combine_csv_files()
    upload_files_to_s3(current_s3)
