"""Tests for load_short_term.py file"""

from pytest import raises
from unittest.mock import MagicMock

from conftest import FakeConn, FakeCursor
from load_short_term import get_db_connection, load_all_data, create_dataframe
from load_short_term import add_availability_ids_to_sensor_df, add_botanist_ids_to_sensor_df
from load_short_term import add_origin_ids_to_plant_df, add_plant_ids_to_sensor_df
from load_short_term import insert_dataframe_into_origin_table, insert_dataframe_into_plant_table
from load_short_term import insert_dataframe_into_sensor_result_table, insert_dataframe_into_botanist_table


def test_get_db_connection(monkeypatch):
    """Verifies that the connection was made"""

    monkeypatch.setattr("psycopg2.connect", lambda **kwargs: None)
    assert get_db_connection(MagicMock()) is None


def test_add_plant_ids_to_sensor_df(fake_dataframe, fake_dataframe_2):
    """"""

    returned_df = add_plant_ids_to_sensor_df(FakeConn(), fake_dataframe, fake_dataframe)
    assert returned_df.equals(fake_dataframe_2)


