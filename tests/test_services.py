from unittest.mock import mock_open, patch

import pytest

from src.services import currency_rates, investment_bank, stock_prices


@patch("src.services.requests.get")
@patch("builtins.open", mock_open(read_data='{"user_currencies": ["USD", "EUR"]}'))
def test_currency_rates(mock_get) -> None:

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


@patch("src.services.requests.get")
@patch("builtins.open", mock_open(read_data='{"user_currencies": ["USD"]}'))
def test_currency_rates_error(mock_get) -> None:
    mock_get.return_value.json.return_value = {"success": False}

    with pytest.raises(ValueError):
        currency_rates()


@patch("src.services.time.sleep")
@patch("src.services.requests.get")
@patch("builtins.open", mock_open(read_data='{"user_stocks": ["AAPL"]}'))
def test_stock_prices(mock_get, mock_sleep) -> None:
    mock_get.return_value.json.return_value = {"Global Quote": {"05. price": "1.1234"}}

    result = stock_prices()

    assert result == [{"stock": "AAPL", "price": 1.12}]
    mock_sleep.assert_called_once_with(1)


@patch("src.services.time.sleep")
@patch("src.services.requests.get")
@patch("builtins.open", mock_open(read_data='{"user_stocks": ["AAPL"]}'))
def test_stock_prices_error(mock_get, mock_sleep) -> None:
    mock_get.return_value.json.return_value = {}

    with pytest.raises(ValueError):
        stock_prices()

    mock_sleep.assert_not_called()


def test_investment_bank() -> None:
    result = investment_bank(
        "2026-10", [{"Дата операции": "2026-10-11", "Сумма операции": 1023}], 100
    )

    assert result == 77


def test_investment_bank_error() -> None:
    result = investment_bank(
        "2026-01", [{"Дата операции": "2026-10-11", "Сумма операции": 1023}], 100
    )

    assert result == 0
