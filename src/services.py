import json

import requests
import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()

api_key = os.getenv("API_KEY")
path = Path(__file__).resolve().parent.parent / "user_settings.json"


url = "https://api.apilayer.com/exchangerates_data/latest"


def currency_rates() -> list[dict]:
    """ Получает курсы выбранных валют через API """

    with open(path, 'r') as file:
        settings = json.load(file)

    currencies = settings["user_currencies"]

    params = {
        "base": "RUB",
        "symbols": ",".join(currencies)
    }

    headers = {
        "apikey": api_key
    }
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
