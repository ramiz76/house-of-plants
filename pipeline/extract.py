"""Extracts all the plant data from plant 0 - 50 and adds to csv file."""
import requests
import pandas as pd


def get_plant_data_by_id(plant_id: int) -> dict:
    """Connects to a corresponding plant endpoint using the given id and return
     a dict of all data for the plant."""

    url = f"https://data-eng-plants-api.herokuapp.com/plants/{plant_id}"

    response = requests.get(url, timeout=10)

    return response.json()


def get_relevant_plant_data() -> list[dict]:
    """Connects to all the endpoints for plants 0 - 50 and adds all relevant data (dict) to a list
    and returns list."""

    list_of_plants = []

    for i in range(51):

        plant = get_plant_data_by_id(i)

        if "error" not in plant.keys():

            relevant_data = {
                "plant_name": plant["name"],
                "scientific_name": plant.get("scientific_name", "unknown"),
                "api_id": plant["plant_id"], "cycle": plant.get("cycle", "unknown"),
                "last_watered": plant["last_watered"], "soil_moisture": plant["soil_moisture"],
                "temperature": plant["temperature"], "sunlight": plant.get("sunlight", "unknown"),
                "recording_taken": plant["recording_taken"],
                "longitude": plant["origin_location"][0],
                "latitude": plant["origin_location"][1],
                "country": plant["origin_location"][3],
                "continent": plant["origin_location"][4].split("/")[0],
                "botanist_name": plant["botanist"]["name"],
                "email": plant["botanist"]["email"], "phone": plant["botanist"]["phone"]
            }

        else:

            relevant_data = {
                "api_id": plant["plant_id"], "error": plant["error"]}

        list_of_plants.append(relevant_data)

    return list_of_plants


def add_to_csv(list_of_plants: list[dict]):
    """Takes a list of plants and add them to a csv file with a row for each plant."""

    dataframe = pd.DataFrame(list_of_plants)
    csv_filename = "plant_data.csv"

    dataframe.to_csv(csv_filename, index=False)


if __name__ == "__main__":

    plants = get_relevant_plant_data()

    add_to_csv(plants)
