"""Modifies data from the csv file and cleans it"""

from datetime import datetime
from os import remove
from re import fullmatch

import pandas as pd


def remove_duplicate_plants(plant_data: pd.DataFrame) -> pd.DataFrame:
    """Returns data-frame without duplicate plants"""

    plant_data.drop_duplicates(subset="plant_name", keep="first", inplace=True)
    return plant_data


def time_format_changed(row: str) -> datetime | None:
    """Returns datatype object from a string
    or None if None entered"""

    try:
        format = "%a, %d %b %Y %H:%M:%S %Z"
        return datetime.strptime(row, format)

    except TypeError:
        return None


def missing_time_fixed(row: str, cache: dict) -> datetime | None:
    """Changes recorded time to a value if None entered
    and always returns a datatype value"""

    try:
        time = datetime.strptime(row, "%Y-%m-%d %H:%M:%S")
        cache["last_time"] = time
        return time

    except TypeError:
        if "last_time" in list(cache.keys()):
            return cache["last_time"]
        return None


def correct_time_recorded(plant_data: pd.DataFrame) -> tuple[pd.DataFrame]:
    """Returns errors recorded after time-recorded is added and
    data-frame object without errors in timestamps"""

    cache_dict = {}
    plant_data["last_watered"] = plant_data["last_watered"].apply(
        time_format_changed)
    plant_data["recording_taken"] = plant_data["recording_taken"].apply(lambda
                            row: missing_time_fixed(row, cache_dict))
    plant_errors = plant_data[plant_data["error"].notnull()]
    plant_data = plant_data[~plant_data["error"].notnull()]
    plant_data = plant_data[plant_data["recording_taken"]
                            >= plant_data["last_watered"]]
    return plant_data, plant_errors


def change_to_numeric(plant_data: pd.DataFrame, columns: str) -> pd.DataFrame:
    """Changes entered columns to a numeric type and removes rows where data
    cannot be numeric for specified columns"""

    for column in columns:
        plant_data[column] = pd.to_numeric(plant_data[column], errors="coerce")
        plant_data = plant_data.dropna(subset=[column])
    return plant_data


def removing_invalid_values(plant_data: pd.DataFrame) -> pd.DataFrame:
    """Returns a data-frame without invalid values in columns"""

    columns_to_numeric = ["soil_moisture",
                          "temperature", "longitude", "latitude"]
    plant_data = change_to_numeric(plant_data, columns_to_numeric)
    plant_data["soil_moisture"] = plant_data[plant_data["soil_moisture"] <= 100 |
                                             plant_data["soil_moisture"] >= 0]
    plant_data["temperature"] = plant_data[plant_data["temperature"] >= -10 |
                                           plant_data["temperature"] <= 39]
    return plant_data


def remove_comma(row: str) -> str:
    """Removes a comma that was noticed
    in the plant name"""

    if row.count(",") >= 1:
        return row.replace(",", "")
    return row


def remove_formatting(row: str) -> str:
    """Removes list format to a string"""

    if row.find("[") != -1:
        return row[2:-2]
    return row


def renaming_values(plant_data: pd.DataFrame) -> pd.DataFrame:
    """Beautifying values in cells and returns edited data-frame"""

    plant_data["plant_name"] = plant_data["plant_name"].apply(remove_comma)
    plant_data["scientific_name"] = plant_data["scientific_name"].apply(
        remove_formatting)
    return plant_data


def find_email(row: str) -> str | None:
    """Finds an email with regex from text"""

    if not isinstance(row, str):
        return
    email_expression = r"((?:(?:[a-z0-9_-]+\.)?)+[a-z0-9_-]+@[a-z0-9_-]+\.[a-z]+(?:\.[a-z]+)?)"
    match = fullmatch(email_expression, row)
    return match.group() if match is not None else None


def find_phone_number(row: str) -> str | None:
    """Finds a phone number with regex from text"""

    number_expression = r"(\+?\(?[0-9-\.]+\)?(?:[x0-9-\.]+)?)"
    match = fullmatch(number_expression, row)
    return match.group().replace(".", "-") if match is not None else None


def verifying_botanist_data(plant_data: pd.DataFrame) -> pd.DataFrame:
    """Verifies the email and phone-number format in the data-frame"""

    plant_data["email"] = plant_data["email"].apply(find_email)
    plant_data["phone"] = plant_data["phone"].apply(
        lambda row: find_phone_number(row) if isinstance(row, str) else None)
    return plant_data


def transform_script() -> None:
    """The main function connection all transform script"""

    time_started = datetime.now()
    print("Transforming...")

    csv_filename = "data/plant_data.csv"
    data = pd.read_csv(csv_filename)
    data.set_index("api_id")
    data, error_rows = correct_time_recorded(data)
    data = renaming_values(data)
    data = remove_duplicate_plants(data)
    data = verifying_botanist_data(data)
    data = pd.concat([error_rows, data])
    remove(csv_filename)
    data.to_csv(csv_filename)

    time_finished = datetime.now()
    print(
        f"Total transformation time: {time_finished - time_started} seconds.")
