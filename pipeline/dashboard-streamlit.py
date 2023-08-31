"""Dashboard to display data from long term storage on S3"""

from os import environ
from datetime import datetime, timezone, timedelta

import streamlit as st
import pandas as pd
from pandas import DataFrame
import seaborn as sns
from dotenv import load_dotenv
from boto3 import client
from botocore.client import BaseClient


TIME_NOW = datetime.now(timezone.utc)


def get_items_in_buckets(s_three: BaseClient, bucket_name: str) -> list[tuple[str]]:
    """Function that finds the list of all items in the bucket"""
    return [(obj["Key"],obj["LastModified"]) for obj
            in s_three.list_objects(Bucket=bucket_name)["Contents"]]


def download_new_files(s_three: BaseClient, bucket_name: str, files: list[tuple[str]]) -> None:
    """Downloading relevant data from the past 6 hrs"""

    for file in files:
        time = TIME_NOW - timedelta(hours=6)
        if file[0][0:14] == "trucks/2023-8/" and file[1] > time:
            time = "-".join([str(TIME_NOW.day),str(TIME_NOW.hour),str(TIME_NOW.minute)])
            s_three.download_file(bucket_name, file[0], f"./streamlit_data/{time}{file[0].split('/')[-1]}")


def get_bucket_connection() -> BaseClient:
    """Returns connection to the AWS buckets"""

    load_dotenv()
    return client("s3", aws_access_key_id = environ.get("ACCESS_KEY"),
                aws_secret_access_key = environ.get("SECRET_KEY"))


def display_frequency_plant_watering(plant_data: DataFrame):
    """"""

    each_plant_last_watered = plant_data["last_watered"].groupby(["plant_name"])
    print(each_plant_last_watered.unique().count())



if __name__ == "__main__":
    # s3_client = get_bucket_connection()
    # bucket = ""
    # all_items = get_items_in_buckets(s3_client, bucket)
    # download_new_files(s3_client, bucket, all_items)
    plants = pd.read_csv("data/plant_data.csv")
    plant_errors = plants[plants["error"].notnull()]
    plant_data = plants[~plants["error"].notnull()]
    display_frequency_plant_watering(plant_data)
