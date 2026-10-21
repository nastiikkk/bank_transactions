from datetime import datetime, timedelta

import pandas as pd

from src.services import currency_rates, stock_prices
from src.utils import convert_dates, read_excel_file


def get_date_range(
    date: str, param: str, earliest_date: datetime
) -> tuple[datetime, datetime]:
    """Определяет начало и конец периода по дате и параметру"""
    date_obj = datetime.strptime(date, "%d.%m.%Y")

    if param == "W":
        week_day = date_obj.weekday()
        date_from = date_obj - timedelta(days=week_day)
    elif param == "M":
        date_from = date_obj.replace(day=1)
    elif param == "Y":
        date_from = date_obj.replace(month=1, day=1)
    elif param == "ALL":
        date_from = earliest_date
    else:
        raise ValueError("Некорректный параметр")
    return date_from, date_obj + timedelta(days=1)


def expenses(
    date_from: datetime, date_to: datetime, data: pd.DataFrame
) -> dict[str, dict]:
    """Рассчитывает расходы за выбранный период и группирует их по категориям"""
    expense_operations = data[
        (data["Сумма операции"] < 0)
        & (data["Дата операции"] >= date_from)
        & (data["Дата операции"] < date_to)
    ]
    total_amount = round(-expense_operations["Сумма операции"].sum())
    groups = (
        expense_operations.groupby("Категория")["Сумма операции"]
        .sum()
        .abs()
        .sort_values(ascending=False)
    )
    transfers_and_cash_groups = (
        groups[groups.index.isin(["Переводы", "Наличные"])]
        .sort_values(ascending=False)
        .to_dict()
    )
    main_groups = groups[~groups.index.isin(["Переводы", "Наличные"])]
    top_categories = main_groups.head(7)
    other_categories = main_groups.iloc[7:]

    main_group = [
        {"category": category, "amount": round(amount)}
        for category, amount in top_categories.items()
    ]

    if not other_categories.empty:
        main_group.append(
            {"category": "Остальное", "amount": round(other_categories.sum())}
        )

    transfers_and_cash = [
        {"category": category, "amount": round(amount)}
        for category, amount in transfers_and_cash_groups.items()
    ]

    return {
        "expenses": {
            "total_amount": total_amount,
            "main": main_group,
            "transfers_and_cash": transfers_and_cash,
        }
    }


def income(
    date_from: datetime, date_to: datetime, data: pd.DataFrame
) -> dict[str, dict]:
    """Рассчитывает поступления за выбранный период и группирует их по категориям"""
    income_operations = data[
        (data["Сумма операции"] > 0)
        & (data["Дата операции"] >= date_from)
        & (data["Дата операции"] < date_to)
    ]
    total_amount = round(income_operations["Сумма операции"].sum())

    main_group = (
        income_operations.groupby("Категория")["Сумма операции"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    main_group = [
        {"category": category, "amount": round(amount)}
        for category, amount in main_group.items()
    ]

    return {"income": {"total_amount": total_amount, "main": main_group}}


def main(date: str, param: str = "M") -> dict:
    operations = convert_dates(read_excel_file())

    earliest_date = operations["Дата операции"].min()
    date_from, date_to = get_date_range(date, param, earliest_date)

    expense = expenses(date_from, date_to, operations)
    incomes = income(date_from, date_to, operations)
    stocks = stock_prices()
    rates = currency_rates()

    return {
        **expense,
        **incomes,
        "currency_rates": rates,
        "stock_prices": stocks,
    }
