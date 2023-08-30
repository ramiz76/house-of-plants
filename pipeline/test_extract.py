"""Tests for extract.py file"""

import pandas as pd
from pytest import raises
from unittest.mock import MagicMock

from conftest import mock_multiprocessing, mock_acquire_plant_data
from extract import acquire_plant_data, get_plant_data_by_id, obtain_relevant_data
from extract import add_to_csv, create_download_folders, add_to_plant_data_list


def test_get_plant_data_by_id(monkeypatch):
    """Verifies that response is correctly processed"""

    fake_response = MagicMock()
    fake_response.json.return_value = {"object": "test"}
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: fake_response)
    returned_data = get_plant_data_by_id(1)
    assert returned_data["object"] == "test"


def test_add_to_csv(monkeypatch, capfd):
    """Verifies that new file is made from a data-frame"""

    list_of_plants = [{"plant":"exists"}]
    dataframe = pd.DataFrame(list_of_plants)
    monkeypatch.setattr("pandas.DataFrame", lambda *args: dataframe)
    monkeypatch.setattr(dataframe, "to_csv", lambda *args, **kwargs: print("File saved!"))
    add_to_csv(list_of_plants)
    captured = capfd.readouterr()

    assert "File saved!" in captured.out


def test_create_download_folders(monkeypatch):
    """Verifies that if directory exists - error is raised"""

    monkeypatch.setattr("os.path.exists", lambda *args: False)
    with raises(FileExistsError):
        create_download_folders()


def test_add_to_plant_data_list(monkeypatch):
    """Verifies that correct data is returned from add_to_plant_data"""

    monkeypatch.setattr("multiprocessing.Pool", mock_multiprocessing)
    monkeypatch.setattr("extract.acquire_plant_data", mock_acquire_plant_data)
    monkeypatch.setattr("extract.NUMBER_OF_PLANTS", 1)

    returned_data = add_to_plant_data_list()

    assert len(returned_data) == 2
    assert all(isinstance(val, dict) for val in returned_data)


def test_acquire_plant_data(monkeypatch):
    """Verifies that correct error is obtained from
    retrieved data"""

    assumed_result = {"api_id": 2, "error": "Missing temperature reading."}
    monkeypatch.setattr("extract.get_plant_data_by_id", mock_acquire_plant_data)
    assert acquire_plant_data(1) == assumed_result


def test_obtain_relevant_data_no_error(fake_plant_data):
    """Verifying that correct data is retrieved"""

    returned_data = obtain_relevant_data(fake_plant_data)
    assert returned_data["plant_name"] == fake_plant_data["name"]
    assert len(list(returned_data.keys())) != len(list(fake_plant_data.keys()))


def test_obtain_relevant_data_with_error():
    """Verifying that error is found"""

    fake_plant_data = {"test": "error", "plant_id": 0}
    assumed_result = {"api_id": 0, "error": "Missing field in data."}
    assert obtain_relevant_data(fake_plant_data) == assumed_result