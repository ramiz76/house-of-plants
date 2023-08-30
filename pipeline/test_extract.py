"""Tests for extract.py file"""

import pandas as pd

from extract import add_to_csv


def test_add_to_csv(monkeypatch, capfd):
    """Verifies that new file is made from a data-frame"""

    list_of_plants = [{"plant":"exists"}]
    dataframe = pd.DataFrame(list_of_plants)
    monkeypatch.setattr("pandas.DataFrame", lambda *args: dataframe)
    monkeypatch.setattr(dataframe, "to_csv", lambda *args, **kwargs: print("File saved!"))
    add_to_csv(list_of_plants)
    captured = capfd.readouterr()

    assert "File saved!" in captured.out
