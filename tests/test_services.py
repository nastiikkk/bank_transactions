import os
from unittest.mock import Mock, mock_open, patch

import pytest
import requests
from dotenv import load_dotenv

from src.services import currency_rates, investment_bank, stock_prices

load_dotenv()

apilayer_api_key = os.getenv("APILAYER_API_KEY")


@patch("src.services.requests.get")
@patch("builtins.open", mock_open(read_data='{"user_currencies": ["USD", "EUR"]}'))
def test_currency_rates(mock_get: Mock) -> None:
    """Проверяет получение и преобразование курсов валют"""

    mock_get.return_value.json.return_value = {
        "success": True,
        "rates": {
            "USD": 0.01,
            "EUR": 0.012,
        },
    }

    result = currency_rates()

    assert result == [
        {"currency": "USD", "rate": 100.0},
        {"currency": "EUR", "rate": 83.33},
    ]

    mock_get.assert_called_once_with(
        "https://api.apilayer.com/exchangerates_data/latest",
        headers={"apikey": apilayer_api_key},
        params={"base": "RUB", "symbols": "USD,EUR"},
    )


@patch("src.services.requests.get")
@patch("builtins.open", mock_open(read_data='{"user_currencies": ["USD"]}'))
def test_currency_rates_error(mock_get: Mock) -> None:
    """Проверяет обработку ошибки при получении курсов валют от API"""
    mock_get.return_value.json.return_value = {"success": False}

    with pytest.raises(ValueError, match="Не удалось получить курсы валют"):
        currency_rates()

    mock_get.assert_called_once_with(
        "https://api.apilayer.com/exchangerates_data/latest",
        headers={"apikey": apilayer_api_key},
        params={"base": "RUB", "symbols": "USD"},
    )


@patch("src.services.requests.get")
@patch("builtins.open", mock_open(read_data='{"user_currencies": ["USD", "EUR"]}'))
def test_currency_rates_http_error(mock_raise: Mock) -> None:
    """Проверяет обработку HTTP-ошибки при запросе курсов валют"""

    mock_raise.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError

    with pytest.raises(requests.exceptions.HTTPError):
        currency_rates()

    mock_raise.return_value.json.assert_not_called()


@patch("src.services.time.sleep")
@patch("src.services.requests.get")
@patch("builtins.open", mock_open(read_data='{"user_stocks": ["AAPL"]}'))
def test_stock_prices(mock_get: Mock, mock_sleep: Mock) -> None:
    """Проверяет получение и округление цен акций"""
    mock_get.return_value.json.return_value = {"Global Quote": {"05. price": "1.1234"}}

    result = stock_prices()

    assert result == [{"stock": "AAPL", "price": 1.12}]
    mock_sleep.assert_called_once_with(1)
    mock_get.assert_called_once()


@patch("src.services.time.sleep")
@patch("src.services.requests.get")
@patch("builtins.open", mock_open(read_data='{"user_stocks": ["AAPL"]}'))
def test_stock_prices_error(mock_get: Mock, mock_sleep: Mock) -> None:
    """Проверяет обработку отсутствия данных о цене акции"""
    mock_get.return_value.json.return_value = {}

    with pytest.raises(ValueError, match="Не удалось получить цену акции"):
        stock_prices()

    mock_sleep.assert_not_called()


def test_investment_bank() -> None:
    """Проверяет расчёт суммы, доступной для инвестирования за месяц"""
    result = investment_bank(
        "2026-10",
        [
            {"Дата операции": "2026-10-11", "Сумма операции": 1023},
            {"Дата операции": "2026-10-23", "Сумма операции": 100},
            {"Дата операции": "2026-10-01", "Сумма операции": 2304},
        ],
        100,
    )

    assert result == 173


def test_investment_bank_transaction_outside_month() -> None:
    """Проверяет, что операции за пределами указанного месяца не учитываются"""
    result = investment_bank(
        "2026-01", [{"Дата операции": "2026-10-11", "Сумма операции": 1023}], 100
    )

    assert result == 0
