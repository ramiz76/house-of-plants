""""""

from datetime import datetime

from pandas import DataFrame
import pandas as pd


def remove_duplicate_plants(plant_data: DataFrame) -> DataFrame:
    """"""
    plant_data.drop_duplicates(subset="plant_name", keep="first", inplace=True)
    return plant_data


def time_format_changed(row: str) -> datetime | None:
    """"""
    try:
        format = "%a, %d %b %Y %H:%M:%S %Z"
        time = datetime.strptime(row, format)
        return time
    except TypeError:
        return None


def missing_time_fixed(row: str, cache: dict) -> datetime:
    """"""
    try:
        time = datetime.strptime(row, "%Y-%m-%d %H:%M:%S")
        cache["last_time"] = time
        return time
    except TypeError:
        return cache["last_time"]


def correct_time_recorded(plant_data: DataFrame) -> tuple[DataFrame]:
    """"""
    cache_dict = {}
    plant_data["last_watered"] = plant_data["last_watered"].apply(time_format_changed)
    plant_data["recording_taken"] = plant_data["recording_taken"].apply(lambda
                        row: missing_time_fixed(row, cache_dict))
    plant_errors = plant_data[plant_data["error"].notnull()]
    plant_data = plant_data[~plant_data["error"].notnull()]
    plant_data = plant_data[plant_data["recording_taken"] >= plant_data["last_watered"]]
    return plant_data, plant_errors


def removing_invalid_values(plant_data: DataFrame) -> DataFrame:
    """"""
    plant_data["soil_moisture"] = plant_data[plant_data["soil_moisture"] <= 100 |
                plant_data["soil_moisture"] >= 0]
    plant_data["temperature"] = plant_data[plant_data["temperature"] >= -10 |
                            plant_data["temperature"] <= 39]
    return plant_data


def remove_comma(row: str) -> str | None:
    """"""
    if row is None:
        return
    else:
        return row.replace(",", "")


def remove_formatting(row: str) -> str:
    """"""
    if row.find("[") != -1:
        return row[2:-2]
    return row


def renaming_values(plant_data: DataFrame) -> DataFrame:
    """"""
    plant_data["plant_name"] = plant_data["plant_name"].apply(remove_comma)
    plant_data["scientific_name"] = plant_data["scientific_name"].apply(remove_formatting)
    return plant_data


if __name__ == "__main__":
    data = pd.read_csv("plant_data.csv")
    data.set_index("api_id")
    data, error_rows = correct_time_recorded(data)
    # pd.concat([error_rows, plant_data]).reset_index()
    data = renaming_values(data)
    data = remove_duplicate_plants(data)