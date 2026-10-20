import pandas as pd

from src.utils import convert_dates, read_excel_file


def test_read_excel_file() -> None:
    result = read_excel_file()

    assert isinstance(result, pd.DataFrame)
    assert not result.empty


def test_convert_dates() -> None:
    data = pd.DataFrame({"Дата операции": ["17.03.2009 23:59:17"]})

    result = convert_dates(data)

    assert result["Дата операции"].iloc[0] == pd.Timestamp("2009-03-17 23:59:17")
