"""Tests for load_short_term.py file"""

from pytest import raises
from unittest.mock import MagicMock

from conftest import FakeConn, FakeCursor
from load_short_term import *


def test_get_db_connection(monkeypatch):
    """Verifies that the connection was made"""

    monkeypatch.setattr("psycopg2.connect", lambda **kwargs: None)
    assert get_db_connection(MagicMock()) is None


def test_add_plant_ids_to_sensor_df(fake_dataframe, fake_dataframe_2):
    """Verifies that None values are kept when received for ids"""

    returned_df = add_plant_ids_to_sensor_df(FakeConn(), fake_dataframe, fake_dataframe)
    assert returned_df.equals(fake_dataframe_2)


def file_removed() -> None:
    """Mocks file removal"""

    print("File removed!")


def test_create_dataframe(monkeypatch, fake_dataframe):
    """Verifies that a new dataframe is created from passed data"""

    monkeypatch.setattr("pandas.read_csv", lambda *args: fake_dataframe)
    monkeypatch.setattr("os.remove", lambda *args: file_removed)

    returned_df = create_dataframe("file")
    assert returned_df.equals(fake_dataframe)


def test_insert_dataframe_into_origin_table(fake_dataframe, capfd):
    """Verifies that execute is ran without errors"""

    insert_dataframe_into_origin_table(FakeConn(), fake_dataframe)
    captured = capfd.readouterr()

    assert "Executed!" in captured.out


def test_insert_dataframe_into_sensor_result_table(fake_dataframe, capfd):
    """Verifies that execute is ran without errors"""

    insert_dataframe_into_sensor_result_table(FakeConn(), fake_dataframe)
    captured = capfd.readouterr()

    assert "Executed!" in captured.out


def test_add_botanist_ids_to_sensor_df(fake_dataframe_2):
    """Verifies that execution has changed the correct things in the dataframe"""

    fake_dataframe_2 = fake_dataframe_2.rename(columns={"api_id": "botanist_id", "plant_id": "phone"})

    returned_df = add_botanist_ids_to_sensor_df(FakeConn(), fake_dataframe_2, fake_dataframe_2)
    assert returned_df["phone"].equals(fake_dataframe_2["phone"])


def test_add_origin_ids_to_plant_df(fake_dataframe_2):
    """Verifies that execution has changed the correct things in the dataframe"""

    fake_dataframe_2 = fake_dataframe_2.rename(columns={"api_id": "latitude", "plant_id": "longitude"})
    fake_connection = MagicMock()
    fake_cursor = fake_connection.cursor().__enter__()
    fake_fetch = fake_cursor.fetchone
    fake_fetch.return_value = {"origin_id": None}
    returned_df = add_origin_ids_to_plant_df(fake_connection, fake_dataframe_2, fake_dataframe_2)
    print(returned_df["origin_id"])
    assert returned_df["origin_id"].isna().sum()


def test_insert_dataframe_into_botanist_table(fake_dataframe, capfd):
    """Verifies that execute is ran without errors"""

    insert_dataframe_into_botanist_table(FakeConn(), fake_dataframe)
    captured = capfd.readouterr()

    assert "Executed!" in captured.out


def test_insert_dataframe_into_plant_table(fake_dataframe, capfd):
    """Verifies that execute is ran without errors"""

    insert_dataframe_into_plant_table(FakeConn(), fake_dataframe)
    captured = capfd.readouterr()

    assert "Executed!" in captured.out


def test_add_availability_ids_to_sensor_df(fake_dataframe_2):
    """Verifies that execution has changed the correct things in the dataframe"""

    fake_dataframe_2 = fake_dataframe_2.rename(columns={"api_id": "error"})
    fake_connection = MagicMock()
    fake_cursor = fake_connection.cursor().__enter__()
    fake_fetch = fake_cursor.fetchone
    fake_fetch.return_value = {"availability_id": None}
    returned_df = add_availability_ids_to_sensor_df(fake_connection, fake_dataframe_2, fake_dataframe_2)
    print(returned_df["availability_id"])
    assert returned_df["availability_id"].isna().sum()