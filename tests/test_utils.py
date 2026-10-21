from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import convert_dates, read_excel_file


def test_read_excel_file() -> None:
    result = read_excel_file()

    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@patch("src.utils.pd.read_excel")
def test_read_excel_file_error(mock_read_excel) -> None:
    mock_read_excel.side_effect = ValueError("Не удалось прочитать файл")

    with pytest.raises(ValueError, match="Не удалось прочитать файл"):
        read_excel_file()


def test_convert_dates() -> None:
    data = pd.DataFrame({"Дата операции": ["17.03.2009 23:59:17"]})

    result = convert_dates(data)

    assert result["Дата операции"].iloc[0] == pd.Timestamp("2009-03-17 23:59:17")


def test_convert_dates_error() -> None:
    data = pd.DataFrame({"Дата операции": ["hello hello"]})

    with pytest.raises(ValueError):
        convert_dates(data)


def test_convert_dates_missed_column() -> None:
    data = pd.DataFrame({"nothing here": ["hello hello"]})

    with pytest.raises(KeyError):
        convert_dates(data)
