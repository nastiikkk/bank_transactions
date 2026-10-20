# import pytest
import pandas as pd

from src.utils import read_excel_file


def test_read_excel_file():
    result = read_excel_file()

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
