from typing import Optional
from dateutil.relativedelta import relativedelta
import pandas as pd
import logging
from datetime import datetime

from src.utils import convert_dates, read_excel_file


def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    if not date:
        date = datetime.now()
    else:
        date = datetime.strptime(date, '%d.%m.%Y')

    date_from = date - relativedelta(months=3)

    transactions = convert_dates(transactions)

    filtered_transactions = transactions[
        (transactions['Дата операции'] >= date_from)
        & (transactions['Дата операции'] <= date)
        & (transactions['Сумма операции'] < 0)
    ]

    days = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье',
    }

    result = (
        filtered_transactions
        .groupby(filtered_transactions['Дата операции'].dt.dayofweek)['Сумма операции']
        .mean()
        .abs()
        .sort_index()
        .rename(index=days)
        .reset_index()
    )

    result.columns = ['День недели', 'Средние траты']

    return result
