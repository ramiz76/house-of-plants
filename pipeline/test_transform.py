""""""

from pytest import fixture
import pandas as pd
from pandas import DataFrame

from transform import remove_duplicate_plants, remove_comma
from transform import remove_formatting, removing_invalid_values
from transform import renaming_values, time_format_changed, missing_time_fixed
from transform import correct_time_recorded, change_to_numeric
from transform import verifying_botanist_data, find_phone_number, find_email


@fixture
def duplicate_data() -> DataFrame:
    return pd.DataFrame(data=[[1,1],[1,2],[1,3]],
        columns=["plant_name","test1"], index=[1,2,3])


def test_remove_duplicate_plants_data_removed(duplicate_data):
    """Verifies that correct amount of data was removed"""
    returned_data = remove_duplicate_plants(duplicate_data)
    assert returned_data.shape == (1,2)


def test_remove_duplicate_plants_data_saved(duplicate_data):
    """Verifies that correct data was saved"""
    returned_data = remove_duplicate_plants(duplicate_data)
    assumed_return = duplicate_data.iloc[0]
    assert returned_data.iloc[0].equals(assumed_return)
    assert returned_data.iloc[1:3].empty
