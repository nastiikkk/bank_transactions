from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.views import expenses, get_date_range, income, main


@pytest.mark.parametrize(
    "param, expected_from",
    [
        ("W", datetime(2026, 10, 19)),
        ("M", datetime(2026, 10, 1)),
        ("Y", datetime(2026, 1, 1)),
        ("ALL", datetime(2017, 1, 1)),
    ],
)
def test_get_date_range(param: str, expected_from: datetime) -> None:
    """Проверяет определение диапазона дат для разных периодов"""
    earliest_date = datetime(2017, 1, 1)

    date_from, date_to = get_date_range("21.10.2026", param, earliest_date)

    assert date_from == expected_from
    assert date_to == datetime(2026, 10, 22)


def test_get_date_range_error() -> None:
    """Проверяет обработку некорректного параметра периода"""
    earliest_date = datetime(2017, 1, 1)
    incorrect_param = "Hello"

    with pytest.raises(ValueError, match="Некорректный параметр"):
        get_date_range("21.10.2026", incorrect_param, earliest_date)


@pytest.fixture
def operations():
    """Создаёт тестовый DataFrame с банковскими операциями"""
    return pd.DataFrame(
        {
            "Дата операции": [
                datetime(2026, 10, 5),
                datetime(2026, 10, 10),
                datetime(2026, 10, 15),
                datetime(2026, 11, 1),
                datetime(2026, 9, 23),
                datetime(2026, 1, 1),
                datetime(2026, 4, 26),
                datetime(2026, 11, 23),
                datetime(2026, 9, 24),
                datetime(2026, 12, 19),
                datetime(2026, 2, 17),
            ],
            "Сумма операции": [
                -100,
                -200,
                500,
                -300,
                -200,
                -50,
                -1000,
                -750,
                -1200,
                -240,
                -130,
            ],
            "Категория": [
                "Продукты",
                "Транспорт",
                "Зарплата",
                "Переводы",
                "Спорт",
                "Одежда",
                "Кино",
                "Наличные",
                "Ремонт",
                "Развлечения",
                "Канцтовары",
            ],
        }
    )


def test_expenses(operations: pd.DataFrame) -> None:
    """Проверяет расчёт расходов и распределение по категориям"""
    date_from = datetime(2026, 1, 1)
    date_to = datetime(2026, 12, 30)
    result = expenses(date_from, date_to, operations)

    assert result == {
        "expenses": {
            "total_amount": 4170,
            "main": [
                {"category": "Ремонт", "amount": 1200},
                {"category": "Кино", "amount": 1000},
                {"category": "Развлечения", "amount": 240},
                {"category": "Спорт", "amount": 200},
                {"category": "Транспорт", "amount": 200},
                {"category": "Канцтовары", "amount": 130},
                {"category": "Продукты", "amount": 100},
                {"category": "Остальное", "amount": 50},
            ],
            "transfers_and_cash": [
                {"category": "Наличные", "amount": 750},
                {"category": "Переводы", "amount": 300},
            ],
        }
    }


def test_expenses_empty_result(operations: pd.DataFrame) -> None:
    """Проверяет результат при отсутствии расходов за период"""
    date_from = datetime(2026, 9, 5)
    date_to = datetime(2026, 9, 9)
    result = expenses(date_from, date_to, operations)

    assert result == {
        "expenses": {
            "total_amount": 0,
            "main": [],
            "transfers_and_cash": [],
        }
    }


def test_expenses_transfers_and_cash(operations: pd.DataFrame) -> None:
    """Проверяет обработку переводов и снятия наличных"""
    date_from = datetime(2026, 11, 1)
    date_to = datetime(2026, 11, 30)
    result = expenses(date_from, date_to, operations)

    assert result == {
        "expenses": {
            "total_amount": 1050,
            "main": [],
            "transfers_and_cash": [
                {"category": "Наличные", "amount": 750},
                {"category": "Переводы", "amount": 300},
            ],
        }
    }


def test_income(operations: pd.DataFrame) -> None:
    """Проверяет расчёт доходов и распределение по категориям"""
    date_from = datetime(2026, 1, 13)
    date_to = datetime(2026, 10, 21)
    result = income(date_from, date_to, operations)

    assert result == {
        "income": {
            "total_amount": 500,
            "main": [{"category": "Зарплата", "amount": 500}],
        }
    }


def test_income_empty_result(operations: pd.DataFrame) -> None:
    """Проверяет результат при отсутствии доходов за период"""
    date_from = datetime(2023, 1, 1)
    date_to = datetime(2024, 1, 1)
    result = income(date_from, date_to, operations)

    assert result == {
        "income": {
            "total_amount": 0,
            "main": [],
        }
    }


@patch("src.views.currency_rates")
@patch("src.views.stock_prices")
@patch("src.views.income")
@patch("src.views.expenses")
@patch("src.views.convert_dates")
@patch("src.views.read_excel_file")
def test_main(
    mock_read_excel: Mock,
    mock_convert_dates: Mock,
    mock_expenses: Mock,
    mock_income: Mock,
    mock_stock_prices: Mock,
    mock_currency_rates: Mock,
) -> None:
    """Проверяет формирование данных главной страницы приложения"""
    operations = pd.DataFrame(
        {
            "Дата операции": [datetime(2026, 10, 10)],
        }
    )

    mock_read_excel.return_value = operations

    mock_convert_dates.return_value = operations

    mock_expenses.return_value = {
        "expenses": {
            "total_amount": 100,
            "main": [{"category": "Продукты", "amount": 100}],
            "transfers_and_cash": [],
        }
    }

    mock_income.return_value = {
        "income": {
            "total_amount": 1000,
            "main": [{"category": "Зарплата", "amount": 1000}],
        }
    }

    mock_stock_prices.return_value = [{"stock": "AAPL", "price": 153.21}]
    mock_currency_rates.return_value = [{"currency": "EUR", "rate": 78.34}]

    result = main("15.10.2026", "M")

    assert result == {
        "expenses": {
            "total_amount": 100,
            "main": [{"category": "Продукты", "amount": 100}],
            "transfers_and_cash": [],
        },
        "income": {
            "total_amount": 1000,
            "main": [{"category": "Зарплата", "amount": 1000}],
        },
        "currency_rates": [{"currency": "EUR", "rate": 78.34}],
        "stock_prices": [{"stock": "AAPL", "price": 153.21}],
    }

    mock_read_excel.assert_called_once_with()
    mock_convert_dates.assert_called_once_with(operations)
    mock_expenses.assert_called_once_with(
        datetime(2026, 10, 1), datetime(2026, 10, 16), operations
    )
    mock_income.assert_called_once_with(
        datetime(2026, 10, 1), datetime(2026, 10, 16), operations
    )
    mock_stock_prices.assert_called_once_with()
    mock_currency_rates.assert_called_once_with()
