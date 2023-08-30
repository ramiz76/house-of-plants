"""Tests for transform.py file"""

from datetime import datetime

import pandas as pd
from pytest import raises

from transform import remove_duplicate_plants, remove_comma
from transform import remove_formatting, removing_invalid_values
from transform import renaming_values, time_format_changed, missing_time_fixed
from transform import correct_time_recorded, change_to_numeric
from transform import verifying_botanist_data, find_phone_number, find_email


def test_remove_duplicate_plants_data_removed(duplicate_data):
    """Verifies that correct amount of data was removed"""

    returned_data = remove_duplicate_plants(duplicate_data)
    assert returned_data.shape == (1, 2)


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
    """Verifies email is not found in incorrectly formatted email"""

    potential_email = "+++++@yahoo.com"
    assert find_email(potential_email) is None


def test_find_email_wront_type():
    """Verifies find_email function returns None
    with wrong type of value entered"""

    assert find_email([]) is None


def test_time_format_changed_incorrect():
    """Verifies None is returned when time-string is
    in incorrect format"""

    assert time_format_changed(None) is None


def test_time_format_changed_correct():
    """Verifies datetype value is returned when time-string
    is in correct format"""

    time_string = "Tue, 29 Aug 2023 13:24:30 GMT"
    assert isinstance(time_format_changed(time_string), datetime)


def test_find_phone_number_correct():
    """Verifies None is returned when incorrectly
    formatted phone number is entered"""

    number = "I am a fake phone number"
    assert find_phone_number(number) is None


def test_find_phone_number_incorrect():
    """Verifies that find_phone_number correctly
    identifies an example phone-number"""

    number = "001-630-832-2711x5822"
    assert find_phone_number(number) == number


def test_change_to_numeric_fully_numeric_df(duplicate_data):
    """Verifies that numeric data is kept"""

    returned_data = change_to_numeric(duplicate_data, ["plant_name"])
    assert not returned_data.iloc[0:3].empty


def test_change_to_numeric_not_fully_numeric_df(duplicate_data):
    """Verifies that non numeric data is removed"""

    extra_row = pd.DataFrame(["not numeric", 2], index=[4, 5])
    duplicate_data = pd.concat([extra_row, duplicate_data])
    returned_data = change_to_numeric(duplicate_data, ["plant_name"])

    with raises(IndexError):
        returned_data.iloc[3]


def test_missing_time_fixed_time():
    """Verifies datetime is changed from a string"""

    time = missing_time_fixed("2023-05-26 12:01:34", {})
    assert isinstance(time, datetime)


def test_missing_time_fixed_not_time():
    """Verifies that None is correctly kept
    as None"""

    time = missing_time_fixed(None, {})
    assert not isinstance(time, datetime)


def test_missing_time_fixed_wrong_type(time_df):
    """Verifying that recording_taken is adjusted with last value if None"""

    cache_dict = {}
    returned_data = time_df["recording_taken"].apply(lambda row: missing_time_fixed(row, cache_dict))
    assert isinstance(returned_data.iloc[-1], datetime)


def test_correct_time_recorded(time_df):
    """Verifying that time is correctly changed"""

    returned_data, error_data = correct_time_recorded(time_df)
    assert error_data.shape == (1, 3)
    assert returned_data.shape == (5, 3)
    assert all(isinstance(returned_data["last_watered"].iloc[i], datetime) for i in range (5))
