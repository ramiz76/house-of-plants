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


TIME_NOW = datetime.now(timezone.utc)


def remove_duplicate_plants(plant_data: pd.DataFrame) -> pd.DataFrame:
    """Returns data-frame without duplicate plants - taken from transform.py"""

    plant_data.drop_duplicates(subset="plant_name", keep="first", inplace=True)
    return plant_data


def dashboard_title() -> None:
    """Creates title for Streamlit dashboard"""

    st.title("House of Plants LMNH Long Term Data Visualisation")
    st.markdown("_Data Visualisation of LMNH plants over time._")


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
def scatter_plot_title() -> None:
    """Creates title for the scatter plot below"""

    st.title("Soil Moisture by Plant")
    st.markdown(
        "### Displays the mean soil moisture level for a selection of plants")


def display_average_soil_moisture(plant_data: pd.DataFrame, plants_to_display: list[str]) -> None:
    """Displays average soil moisture for selected plants"""

    plant_data = plant_data.copy()
    plt.figure(figsize=(12, 8))

    chosen_plants = plant_data[plant_data["plant_name"].isin(
        plants_to_display)]
    each_plant_soil_moisture = chosen_plants.groupby(["plant_name"])[
        "soil_moisture"]
    average_soil_moisture_for_each_plant = each_plant_soil_moisture.mean()
    scatterplot_graph = sns.scatterplot(
        data=average_soil_moisture_for_each_plant)
    st.write(scatterplot_graph.figure)


def bar_chart_title() -> None:
    """Creates title for the bar chart below"""

    st.title("Number of errors for each plant")
    st.markdown("API ID refers to the API endpoint for each plant")


def display_which_plants_get_errors(plant_data_errors: pd.DataFrame) -> None:
    """Displays bar-plot of errors by plant id"""

    plant_data_errors = plant_data_errors.copy()
    plt.figure()

    each_plant_error = plant_data_errors.groupby(["api_id"], as_index=True)
    error_count = each_plant_error.count().reset_index()
    barplot_graph = sns.barplot(data=error_count, x="api_id", y="error")
    st.write(barplot_graph.figure)


def pie_chart_title() -> None:
    """Creates title for the pie chart below"""

    st.title("Plants by Country")
    st.markdown("")


def display_pie_chart_continents(plant_data: pd.DataFrame) -> None:
    """Displays the pie-chart of continents for the plant origin
    that are displayed in the museum"""

    plant_data = plant_data.copy()

    plt.figure()

    keys = plant_data["continent"].unique()

    unique_plants = remove_duplicate_plants(plant_data)
    plant_continents = unique_plants[["continent"]].value_counts()

    sns.color_palette("tab20")
    plot = plant_continents.plot(kind="pie", y=keys, autopct="%.2f%%")
    st.write(plot.figure)


def average_temp_title() -> None:
    """Creates title text for the average temperature bar graph below"""

    st.title("Average Temperature by region")
    st.markdown(
        "Displays the average temperature readings for plants native to different regions")


def display_temp_bar_chart(plant_data: pd.DataFrame) -> None:
    """Constructs a bar chart of average temperature, grouped by region"""

    plant_data = plant_data.copy()

    plt.figure()

    st.dataframe(plant_data)


if __name__ == "__main__":
    # s3_client = get_bucket_connection()
    # bucket = ""
    # all_items = get_items_in_buckets(s3_client, bucket)
    # download_new_files(s3_client, bucket, all_items)

    dashboard_title()
    plant_df = pd.read_csv("pipeline/combined.csv")
    plant_error_df = plant_df[plant_df["error"] != "No Error"]
    plant_df = plant_df[plant_df["error"] == "No Error"]

    # display_frequency_plant_watering(plant_data)
    plants_to_display = ["Epipremnum Aureum",
                         "Venus flytrap", "Cactus", "Rafflesia arnoldii", "Corpse flower", "Wollemi pine"]

    scatter_plot_title()
    display_average_soil_moisture(plant_df, plants_to_display)

    bar_chart_title()
    display_which_plants_get_errors(plant_error_df)

    pie_chart_title()
    display_pie_chart_continents(plant_df)

    average_temp_title()
    display_temp_bar_chart(plant_df)
