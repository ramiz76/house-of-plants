"""Dashboard to display data from long term storage on S3"""

from os import environ
from datetime import datetime, timezone, timedelta

from boto3 import client
from botocore.client import BaseClient
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from transform import remove_duplicate_plants


TIME_NOW = datetime.now(timezone.utc)


def get_items_in_buckets(s_three: BaseClient, bucket_name: str) -> list[tuple[str]]:
    """Function that finds the list of all items in the bucket"""

    return [(obj["Key"], obj["LastModified"]) for obj
            in s_three.list_objects(Bucket=bucket_name)["Contents"]]


def download_new_files(s_three: BaseClient, bucket_name: str, files: list[tuple[str]]) -> None:
    """Downloading relevant data from the past 6 hrs"""

    for file in files:
        time = TIME_NOW - timedelta(hours=6)
        if file[0][0:14] == "trucks/2023-8/" and file[1] > time:
            time = "-".join([str(TIME_NOW.day),
                            str(TIME_NOW.hour), str(TIME_NOW.minute)])
            s_three.download_file(
                bucket_name, file[0], f"./streamlit_data/{time}{file[0].split('/')[-1]}")


def get_bucket_connection() -> BaseClient:
    """Returns connection to the AWS buckets"""

    load_dotenv()
    return client("s3", aws_access_key_id=environ.get("ACCESS_KEY"),
                  aws_secret_access_key=environ.get("SECRET_KEY"))


# def display_frequency_plant_watering(plant_data: DataFrame):
#     """"""

#     each_plant_last_watered = plant_data.groupby(["plant_name"])["last_watered"]
#     all_watered_times_for_plants = each_plant_last_watered.unique()
#     print((all_watered_times_for_plants))
#     for row in (all_watered_times_for_plants):
#         print((row), row.index)


def display_average_soil_moisture(plant_data: pd.DataFrame, plants_to_display: list[str]) -> None:
    """Displays average soil moisture for selected plants"""

    chosen_plants = plant_data[plant_data["plant_name"].isin(
        plants_to_display)]
    each_plant_soil_moisture = chosen_plants.groupby(["plant_name"])[
        "soil_moisture"]
    average_soil_moisture_for_each_plant = each_plant_soil_moisture.mean()
    scatterplot_graph = sns.scatterplot(
        data=average_soil_moisture_for_each_plant)
    st.write(scatterplot_graph.figure)


def display_which_plants_get_errors(plant_data_errors: pd.DataFrame) -> None:
    """Displays bar-plot of errors by plant id"""

    each_plant_error = plant_data_errors.groupby(["api_id"], as_index=True)
    error_count = each_plant_error.count().reset_index()
    barplot_graph = sns.barplot(data=error_count, x="api_id", y="error")
    st.write(barplot_graph.figure)


def display_pie_chart_continents(plant_data: pd.DataFrame) -> None:
    """Displays the pie-chart of continents for the plant origin
    that are displayed in the museum"""

    keys = plant_data["continent"].unique()
    unique_plants = remove_duplicate_plants(plant_data)
    plant_continents = unique_plants[["continent"]].value_counts()

    continent_plant_pie_chart = plt.pie(plant_continents, labels=keys)
    st.write(continent_plant_pie_chart.figure)


if __name__ == "__main__":
    # s3_client = get_bucket_connection()
    # bucket = ""
    # all_items = get_items_in_buckets(s3_client, bucket)
    # download_new_files(s3_client, bucket, all_items)
    plants = pd.read_csv("combined.csv")
    plant_errors = plants[plants["error"].notnull()]
    plant_data = plants[~plants["error"].notnull()]
    # display_frequency_plant_watering(plant_data)
    plants_to_display = ["Epipremnum Aureum", "Venus flytrap", "Cactus"]
    # display_average_soil_moisture(plant_data, plants_to_display)
    # display_which_plants_get_errors(plant_errors)
    display_pie_chart_continents(plant_data)
