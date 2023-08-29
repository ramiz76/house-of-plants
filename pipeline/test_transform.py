"""Tests for transform.py file"""

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
    """Returns a data-frame with duplicate data"""
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


def test_remove_comma_no_comma():
    """Verifies that text is kept the same if without a comma"""
    text = "Text without comma"
    assert remove_comma(text) == text


def test_remove_comma_comma_exists():
    """Verifying that comma removal was correct"""
    text = "Text with a comma,"
    assert remove_comma(text) == text[:-1]


def test_remove_formatting():
    """Test that verifies correct formatting on 'scientific_name' column"""
    formatted_text = "['Some text added']"
    not_formatted_text = "Some text added"
    assert remove_formatting(formatted_text) == not_formatted_text
    assert remove_formatting(not_formatted_text) == not_formatted_text


def test_find_email_correct():
    """Verifies correct email is found"""
    potential_email = "test.email@yahoo.com"
    assert find_email(potential_email) == potential_email


def test_find_email_incorrect():
    """Verifies email is not found in incorrect formatted email"""
    potential_email = "+++++@yahoo.com"
    assert find_email(potential_email) is None


def test_find_email_wront_type():
    """Verifies find_email function returns None
    with wrong type of value entered"""
    assert find_email([]) is None