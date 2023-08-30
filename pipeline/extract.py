"""Extracts all the plant data from plant 0 - 50 and adds to csv file"""

import os
import time

import pandas as pd
import requests


PLANTS_ON_DISPLAY = 50


def get_plant_data_by_id(plant_id: int) -> dict:
    """Connects to a corresponding plant endpoint using the given id and return
     a dict of all data for the plant"""

    url = f"https://data-eng-plants-api.herokuapp.com/plants/{plant_id}"
    try:
        response = requests.get(url, timeout=5).json()

    except requests.exceptions.Timeout:
        response = {
            "error": "Timeout: The request could not be completed.", "plant_id": plant_id}
    return response


def obtain_relevant_data(plant: dict) -> dict:
    """Obtains only the relevant data from the plant api and returns as a dict"""

    try:
        relevant_data = {
            "plant_name": plant["name"],
            "scientific_name": plant.get("scientific_name", "unknown"),
            "api_id": plant["plant_id"], "cycle": plant.get("cycle", "unknown"),
            "last_watered": plant.get("last_watered", None), "soil_moisture": plant.get("soil_moisture", None),
            "temperature": plant.get("temperature", None), "sunlight": plant.get("sunlight", "unknown"),
            "recording_taken": plant.get("recording_taken", None),
            "longitude": plant["origin_location"][0],
            "latitude": plant["origin_location"][1],
            "country": plant["origin_location"][3],
            "continent": plant["origin_location"][4].split("/")[0],
            "botanist_name": plant["botanist"]["name"],
            "email": plant["botanist"]["email"], "phone": plant["botanist"]["phone"]
        }

    except:
        relevant_data = {
            "api_id": plant["plant_id"], "error": "Missing field in data."}
    return relevant_data


def get_relevant_plant_data() -> list[dict]:
    """Connects to all the endpoints for plants 0 - 50 and adds all relevant data (dict) to a list
    and returns list"""

    list_of_plants = []

    for i in range(PLANTS_ON_DISPLAY + 1):
        plant = get_plant_data_by_id(i)
        if "error" not in plant.keys():
            if plant["temperature"] is None:
                relevant_data = {
                    "api_id": plant["plant_id"], "error": "Missing temperature reading."}
            elif plant["soil_moisture"] is None:
                relevant_data = {
                    "api_id": plant["plant_id"], "error": "Missing soil_moisture reading."}
            else:
                relevant_data = obtain_relevant_data(plant)
        else:
            relevant_data = {
                "api_id": plant["plant_id"], "error": plant["error"]}
        list_of_plants.append(relevant_data)

    return list_of_plants


def create_download_folders() -> None:
    """Creates a folder with the name "extracted_data" if it doesn't already exist"""

    folder_exists = os.path.exists("extracted_data")
    if not folder_exists:
        os.makedirs("extracted_data")


def add_to_csv(list_of_plants: list[dict]):
    """Takes a list of plants and add them to a csv file with a row for each plant"""

    dataframe = pd.DataFrame(list_of_plants)
    csv_filename = "extracted_data/plant_data.csv"
    dataframe.to_csv(csv_filename, index=False)


def extract_and_create_csv():

    start_time = time.time()
    print("Extracting...")

    plants = get_relevant_plant_data()
    create_download_folders()
    add_to_csv(plants)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total extraction time: {elapsed_time:.2f} seconds.")
