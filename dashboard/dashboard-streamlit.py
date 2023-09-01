"""Dashboard to display data from long term storage on S3"""

from os import environ, path, remove
from datetime import datetime, timedelta

from boto3 import client
from botocore.client import BaseClient
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


@st.cache_data(ttl="30s")
def fetch_data():
    """Streamlit Cache"""

    s3_client = get_bucket_connection()
    bucket = environ.get("BUCKET_NAME")
    items_in_bucket = get_items_in_buckets(s3_client, bucket)

    if "full_s3_data.csv" in items_in_bucket:
        download_new_version(s3_client, bucket)
    st.session_state['last_fetch_time'] = datetime.now()
    data = pd.read_csv("combined.csv")
    return data


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

    if "Contents" in list(s_three.list_objects(Bucket=bucket_name).keys()):
        return [obj["Key"] for obj in s_three.list_objects(Bucket=bucket_name)["Contents"]]
    return []


def download_new_version(s_three: BaseClient, bucket_name: str) -> None:
    """Downloading relevant data from the S3 bucket"""

    filepath = "combined.csv"
    if path.exists(filepath):
        remove(filepath)
    s_three.download_file(bucket_name, "full_s3_data.csv", filepath)


def get_bucket_connection() -> BaseClient:
    """Returns connection to the AWS buckets"""

    load_dotenv()
    return client("s3", aws_access_key_id=environ.get("ACCESS_KEY"),
                  aws_secret_access_key=environ.get("SECRET_KEY"))


def scatter_plot_title() -> None:
    """Creates title for the scatter plot below"""

    st.title("Soil Moisture by Plant")
    st.markdown(
        "### Displays the mean soil moisture level for a selection of plants")


def get_moisture_changes_by_time(plant_data: pd.DataFrame, plants_to_display: list[str]) -> None:
    """Displays data for chosen plants for moisture changes by time"""

    plant_data["recording_taken"] = pd.to_datetime(
        plant_data["recording_taken"])
    plant_data_lineplot = plant_data[plant_data["plant_name"].isin(
        plants_to_display)][["plant_name", "recording_taken", "soil_moisture"]]
    grouped_data = plant_data_lineplot.groupby("plant_name")

    fig, axis = plt.subplots()

    for plant, data in grouped_data:
        sns.lineplot(data=data, y="soil_moisture",
                     x="recording_taken", label=plant, ax=axis)

    axis.set_title("Soil Moisture Over Time")
    axis.set_xlabel("Recording Taken")
    axis.set_ylabel("Soil Moisture")

    axis.legend()
    st.pyplot(fig)


def soil_over_time_for_each_plant_title() -> None:
    """Creates title for the bar chart below"""

    st.title("Soil moisture changes recorded")
    st.markdown("Choose the plants for this graph to display")


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
    st.write(plant_data_errors)
    plt.figure()

    each_plant_error = plant_data_errors.groupby(["api_id"], as_index=True)
    st.write(each_plant_error)
    error_count = each_plant_error.count().reset_index()
    barplot_graph = sns.barplot(data=error_count, x="api_id", y="error")
    st.write(barplot_graph.figure)


def pie_chart_title() -> None:
    """Creates title for the pie chart below"""

    st.markdown("## Plants by Country")


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

    st.title("Plants by region - Temperature Averages")
    st.markdown(
        "Displays the Mean, Median and Standard Deviations of temperature\
              readings for plants native to different regions, as well as\
                  breakdown of percentage of plants from each region")


def mean_temp_title() -> None:
    """Creates title text for the mean temperature bar graph below"""

    st.markdown(
        "## Mean temperature by region")


def display_temp_mean_bar_chart(plant_data: pd.DataFrame) -> None:
    """Constructs a bar chart of mean temperature, grouped by region"""

    plant_data = plant_data.copy()

    plt.figure()

    mean_temps = plant_data.groupby(["continent"], as_index=False)[
        "temperature"].mean()

    temp_bars = sns.barplot(mean_temps, x="continent", y="temperature")
    plt.ylabel('mean temperature')
    st.write(temp_bars.figure)


def median_temp_title() -> None:
    """Creates title text for the median temperature bar graph below"""

    st.markdown(
        "## Median temperature by region")


def display_temp_median_bar_chart(plant_data: pd.DataFrame) -> None:
    """Constructs a bar chart of mean temperature, grouped by region"""

    plant_data = plant_data.copy()

    plt.figure()

    mean_temps = plant_data.groupby(["continent"], as_index=False)[
        "temperature"].median()

    temp_bars = sns.barplot(mean_temps, x="continent", y="temperature")
    plt.ylabel('median temperature')
    st.write(temp_bars.figure)


def std_temp_title() -> None:
    """Creates title text for the standard deviation temperature bar graph below"""

    st.markdown(
        "## Standard Deviation temperature by region")


def display_temp_std_bar_chart(plant_data: pd.DataFrame) -> None:
    """Constructs a bar chart of standard deviation temperature, grouped by region"""

    plant_data = plant_data.copy()

    plt.figure()

    mean_temps = plant_data.groupby(["continent"], as_index=False)[
        "temperature"].std()

    temp_bars = sns.barplot(mean_temps, x="continent", y="temperature")
    plt.ylabel('temperature standard deviation')
    st.write(temp_bars.figure)


if __name__ == "__main__":

    dashboard_title()
    plant_df = fetch_data()
    plant_error_df = plant_df[plant_df["error"] != "No Error"]

    plant_df = plant_df[plant_df["error"] == "No Error"]

    plants_to_display = st.sidebar.multiselect("Select Plant(s) for the graphs",
                options=plant_df["plant_name"].unique(), default=plant_df["plant_name"].unique()[1])

    scatter_plot_title()
    display_average_soil_moisture(plant_df, plants_to_display)

    # Breaks when we have no errors
    # bar_chart_title()
    # display_which_plants_get_errors(plant_error_df)

    # Title for averages section
    average_temp_title()
    r, l = st.columns(2)
    with r:
        pie_chart_title()
        display_pie_chart_continents(plant_df)

        mean_temp_title()
        display_temp_mean_bar_chart(plant_df)

    with l:
        median_temp_title()
        display_temp_median_bar_chart(plant_df)

        std_temp_title()
        display_temp_std_bar_chart(plant_df)

    # Soil moisture changes over time graph
    soil_over_time_for_each_plant_title()
    get_moisture_changes_by_time(plant_df, plants_to_display)
