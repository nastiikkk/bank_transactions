from pathlib import Path

import pandas as pd

path = Path(__file__).resolve().parent.parent / "data" / "operations.xlsx"


def read_excel_file() -> pd.DataFrame:
    df = pd.read_excel(path)
    return df


def convert_dates(data: pd.DataFrame) -> pd.DataFrame:
    """Преобразует строки с датами в объекты datetime"""
    data["Дата операции"] = pd.to_datetime(
        data["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    )
    return data
