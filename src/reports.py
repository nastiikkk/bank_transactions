import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import convert_dates

path = Path(__file__).resolve().parent.parent / "logs" / "reports.log"

logger = logging.getLogger("reports")
file_handler = logging.FileHandler(path, "w", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel("DEBUG")


def spending_by_weekday(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> pd.DataFrame:

    if not date:
        date = datetime.now()
    else:
        date = datetime.strptime(date, "%d.%m.%Y")

    date_to = date + relativedelta(days=1)
    date_from = date - relativedelta(months=3)

    transactions = convert_dates(transactions)

    logger.info("Начата фильтрация транзакций")

    filtered_transactions = transactions[
        (transactions["Дата операции"] >= date_from)
        & (transactions["Дата операции"] < date_to)
        & (transactions["Сумма операции"] < 0)
    ]

    days = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье",
    }

    result = (
        filtered_transactions.groupby(
            filtered_transactions["Дата операции"].dt.dayofweek
        )["Сумма операции"]
        .mean()
        .abs()
        .sort_index()
        .rename(index=days)
        .reset_index()
    )

    result.columns = ["День недели", "Средние траты"]

    logger.info("Фильтрация транзакций завершена")

    return result
