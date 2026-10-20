import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()

apilayer_api_key = os.getenv("APILAYER_API_KEY")
alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_ACCESS_KEY")
path = Path(__file__).resolve().parent.parent / "user_settings.json"


def currency_rates() -> list[dict]:
    """Получает курсы выбранных валют через API"""

    with open(path, "r") as file:
        settings = json.load(file)

    currencies = settings["user_currencies"]

    url = "https://api.apilayer.com/exchangerates_data/latest"

    params = {"base": "RUB", "symbols": ",".join(currencies)}

    headers = {"apikey": apilayer_api_key}
    response = requests.get(url, headers=headers, params=params)

    response.raise_for_status()

    response = response.json()

    if response.get("success") is False:
        raise ValueError("Не удалось получить курсы валют")

    rates = response["rates"]
    return [
        {"currency": currency, "rate": round(1 / rates[currency], 2)}
        for currency in currencies
    ]


def stock_prices() -> list:
    """Получает стоимость акций из S&P 500 через API"""
    with open(path, "r") as file:
        settings = json.load(file)
    stocks = settings["user_stocks"]

    url = "https://www.alphavantage.co/query"

    prices = []

    for stock in stocks:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": stock,
            "apikey": alpha_vantage_api_key,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        response = response.json()
        quote = response.get("Global Quote")

        if not quote:
            raise ValueError("Не удалось получить цену акции")

        prices.append({"stock": stock, "price": round(float(quote["05. price"]), 2)})
        time.sleep(1)

    return prices


def investment_bank(
    month: str, transactions: List[Dict[str, Any]], limit: int
) -> float:
    date_obj = datetime.strptime(month, "%Y-%m")

    can_save = 0

    for transaction in transactions:
        transaction["Дата операции"] = datetime.strptime(
            transaction["Дата операции"], "%Y-%m-%d"
        )
        transaction_date = transaction["Дата операции"]
        if (
            transaction_date.year == date_obj.year
            and transaction_date.month == date_obj.month
        ):
            amount = transaction["Сумма операции"]
            rounded_amount = ((amount + limit - 1) // limit) * limit
            can_save += rounded_amount - amount

    return can_save
