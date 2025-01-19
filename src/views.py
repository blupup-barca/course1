# -*- coding: utf-8 -*-

import json

import pandas as pd

from src.logger import setting_logger
from src.utils import (fetch_exchange_rates, fetch_stock_prices, filter_transactions_by_card,
                       filter_transactions_by_date, get_top_five_transactions, greeting)

logger = setting_logger("views")


def generator_json_data(df_transactions: pd.DataFrame, date_filter: str) -> str:
    """Функция формирует json ответ для главной страницы SkyBank"""
    logger.info("Функция начала свою работу.")
    greeting_ = greeting()
    filter_transactions_by_date_ = filter_transactions_by_date(df_transactions, date_filter)
    filter_transactions_by_card_ = filter_transactions_by_card(filter_transactions_by_date_)
    top_five_transactions = get_top_five_transactions(filter_transactions_by_date_)
    exchange_rates = fetch_exchange_rates()
    stock_prices = fetch_stock_prices()

    json_data = json.dumps(
        {
            "greeting": greeting_,
            "cards": filter_transactions_by_card_,
            "top_transactions": top_five_transactions,
            "currency_rates": exchange_rates,
            "stock_prices": stock_prices,
        },
        indent=4,
        ensure_ascii=False,
    )
    logger.info("Функция успешно завершила свою работу.")
    return json_data
