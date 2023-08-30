"""Conftest file with fixtures and mocking classes"""

from pytest import fixture
import pandas as pd


@fixture
def duplicate_data() -> pd.DataFrame:
    """Returns a data-frame with duplicate data"""

    return pd.DataFrame(data=[["1", 1], ["1", 2], ["1", 3]], 
        columns=["plant_name", "test1"], index=[1, 2, 3])


@fixture
def time_df() -> pd.DataFrame:
    """Returns a testing data-frame with time-strings columns"""

    data = [[f"2023-05-26 12:0{i}:34", f"Tue, 29 Jan 2023 13:2{i}:30 GMT", None] for i in range (5)]
    data.append([None, None, "error found"])
    return pd.DataFrame(data=data, 
        columns=["recording_taken", "last_watered", "error"], index=[1, 2, 3, 4, 5, 6])