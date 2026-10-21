import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import convert_dates
from functools import wraps
from typing import Any, Callable, Optional


path_to_log = Path(__file__).resolve().parent.parent / "logs" / "reports.log"

logger = logging.getLogger("reports")
file_handler = logging.FileHandler(path_to_log, "w", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel("DEBUG")


def save_report(
    func: Optional[Callable] = None,
    filename: str = "weekday_report.csv",
) -> Callable:
    """Сохраняет результат функции-отчёта в CSV-файл."""

    def decorator(report_func: Callable) -> Callable:
        @wraps(report_func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            result = report_func(*args, **kwargs)

            path_to_report = Path(__file__).resolve().parent.parent / "reports" / filename

            result.to_csv(path_to_report, index=False, encoding="utf-8")

            return result

        return wrapper

    if func is not None:
        return decorator(func)

    return decorator

@save_report
def spending_by_weekday(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> pd.DataFrame:
    """Возвращает средние траты в каждый из дней недели за последние три месяца"""
    if date is None:
        date_obj = datetime.now()
    else:
        date_obj = datetime.strptime(date, "%d.%m.%Y")

    date_to = date_obj + relativedelta(days=1)
    date_from = date_obj - relativedelta(months=3)

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
