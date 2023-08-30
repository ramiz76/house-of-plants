"""Tests for extract.py file"""

import pandas as pd
from pytest import raises

from conftest import mock_multiprocessing, mock_acquire_plant_data
from extract import acquire_plant_data
from extract import add_to_csv, create_download_folders, add_to_plant_data_list


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
    """"""

    assumed_result = {"api_id": 2, "error": "Missing temperature reading."}
    monkeypatch.setattr("extract.get_plant_data_by_id", mock_acquire_plant_data)
    assert acquire_plant_data(1) == assumed_result