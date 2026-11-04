import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()

exchangerate_api_key = os.getenv("EXCHANGERATE_API_KEY")
alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_ACCESS_KEY")
path = Path(__file__).resolve().parent.parent / "user_settings.json"


path_to_log = Path(__file__).resolve().parent.parent / "logs" / "services.log"
logger = logging.getLogger("services")
file_handler = logging.FileHandler(path_to_log, "w", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel("DEBUG")


def currency_rates() -> list[dict]:
    """Получает курсы выбранных валют через API"""

    with open(path, "r") as file:
        settings = json.load(file)

    currencies = settings["user_currencies"]

    if exchangerate_api_key is None:
        raise ValueError("EXCHANGERATE_API_KEY не найден в переменных окружения")

    url = (
        f"https://v6.exchangerate-api.com/v6/"
        f"{exchangerate_api_key}/latest/RUB"
    )
    response = requests.get(url)

    response.raise_for_status()

    response = response.json()

    if response.get("result") != "success":
        raise ValueError("Не удалось получить курсы валют")

    rates = response["conversion_rates"]
    return [
        {"currency": currency, "rate": round(1 / rates[currency], 2)}
        for currency in currencies
    ]


def stock_prices() -> list[dict]:
    """Получает стоимость акций из S&P 500 через API"""
    if alpha_vantage_api_key is None:
        raise ValueError("ALPHA_VANTAGE_ACCESS_KEY не найден в переменных окружения")
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
    """Возвращает сумму, которую удалось бы отложить в «Инвесткопилку»"""
    logger.info("Начат расчет накоплений за месяц")
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

            logger.debug(
                f"Операция за {transaction_date}: сумма {amount}, накоплено {rounded_amount-amount}",
            )
    logger.info(f"Расчёт накоплений за месяц завершен. Итого: {can_save}")

    return can_save
