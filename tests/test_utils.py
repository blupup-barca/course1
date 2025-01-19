import json
import unittest
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest
from freezegun import freeze_time

from src.utils import (fetch_exchange_rates, fetch_stock_prices, filter_transactions_by_card,
                       filter_transactions_by_date, get_top_five_transactions, greeting, read_xlsx_file)


# Тест функции read_xlsx_file
@patch("pandas.read_excel")
def test_read_xlsx_file(mock_read_excel: unittest.mock.MagicMock) -> None:
    test_data = {"Column1": [1, 2, 3], "Column2": ["A", "B", "C"]}
    expected_df = pd.DataFrame(test_data)
    mock_read_excel.return_value = expected_df
    print(type(mock_read_excel))
    result_df = read_xlsx_file("dummy_path.xlsx")
    pd.testing.assert_frame_equal(result_df, expected_df)
    mock_read_excel.assert_called_once_with("dummy_path.xlsx")


# Тест функции get_greeting
@freeze_time("2024-01-01 07:00:00")
def test_greeting_morning() -> None:
    assert greeting() == "Доброе утро"


@freeze_time("2024-01-01 13:00:00")
def test_get_greeting_day() -> None:
    assert greeting() == "Добрый день"


@freeze_time("2024-01-01 19:00:00")
def test_get_greeting_evening() -> None:
    assert greeting() == "Добрый вечер"


@freeze_time("2024-01-01 00:00:00")
def test_get_greeting_night() -> None:
    assert greeting() == "Доброй ночи"


# Тест функции get_top_five_transactions
class TestGetTopFiveTransactions(unittest.TestCase):
    def setUp(self) -> None:
        self.transactions_data = {
            "Дата операции": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06"],
            "Сумма операции": [100, 200, 300, 400, 500, 600],
            "Категория": ["A", "B", "C", "D", "E", "F"],
            "Описание": ["desc1", "desc2", "desc3", "desc4", "desc5", "desc6"],
        }
        self.transactions_df = pd.DataFrame(self.transactions_data)

    def test_get_top_five_transactions(self) -> None:
        expected_output = [
            {
                "date": "2023-01-06",
                "amount": 600,
                "category": "F",
                "description": "desc6",
            },
            {
                "date": "2023-01-05",
                "amount": 500,
                "category": "E",
                "description": "desc5",
            },
            {
                "date": "2023-01-04",
                "amount": 400,
                "category": "D",
                "description": "desc4",
            },
            {
                "date": "2023-01-03",
                "amount": 300,
                "category": "C",
                "description": "desc3",
            },
            {
                "date": "2023-01-02",
                "amount": 200,
                "category": "B",
                "description": "desc2",
            },
        ]

        actual_output = get_top_five_transactions(self.transactions_df)
        self.assertEqual(actual_output, expected_output)

    def test_empty_dataframe(self) -> None:
        empty_df = pd.DataFrame(columns=["Дата операции", "Сумма операции", "Категория", "Описание"])
        self.assertIsNone(get_top_five_transactions(empty_df))


# Тест функции  fetch_exchange_rates
class TestFetchExchangeRates(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
    @patch("os.getenv", return_value="mock_api_key")
    @patch("requests.get")
    def test_fetch_exchange_rates(
        self, mock_get: unittest.mock.MagicMock, mock_env: unittest.mock.MagicMock, mock_open: unittest.mock.MagicMock
    ) -> None:
        mock_get.return_value.json.return_value = {"conversion_rates": {"RUB": 1, "EUR": 0.01073, "USD": 0.01168}}
        expected_result = [{"EUR": 93.2}, {"USD": 85.62}]
        result = fetch_exchange_rates()
        self.assertEqual(result, expected_result)
        mock_get.assert_called_once_with("https://v6.exchangerate-api.com/v6/mock_api_key/latest/RUB")


# Тест функции fetch_stock_prices
class TestFetchStockPrices(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"user_stocks": ["AAPL", "GOOGL"]}))
    @patch("os.getenv", side_effect=lambda k: "mock_api_key" if k == "API_KEY_STOCK_PRICE" else None)
    @patch("requests.get")
    def test_fetch_stock_prices(
        self, mock_get: unittest.mock.MagicMock, mock_env: unittest.mock.MagicMock, mock_open: unittest.mock.MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"Global Quote": {"05. price": "150.00"}}
        mock_get.return_value = mock_response
        expected_output = [{"AAPL": 150.0}, {"GOOGL": 150.0}]
        actual_output = fetch_stock_prices()
        self.assertEqual(actual_output, expected_output)
        self.assertEqual(mock_get.call_count, 2)


# Тест функции filter_transactions_by_card
@pytest.fixture
def test_filter_transactions_by_card(sample_transactions: pd.DataFrame) -> None:
    result = filter_transactions_by_card(sample_transactions)
    expected_result = [
        {"last_digits": "5678", "total_spent": 3000, "cashback": 30.0},
        {"last_digits": "4321", "total_spent": 1500, "cashback": 15.0},
    ]
    assert result == expected_result


# Тест функции filter_transactions_by_date
@pytest.fixture
def test_filter_transactions_by_date(transactions_list: pd.DataFrame) -> None:
    result = filter_transactions_by_date(transactions_list, "30.11.2023 23:00:00").to_dict()
    expected = {"Дата операции": {2: "21.11.2023 10:00:00"}, "Сумма": {2: 300}, "Описание": {2: "Транзакция 3"}}
    assert result == expected


@pytest.fixture
def test_filter_transactions_by_date_no_date(transactions_list: pd.DataFrame) -> None:
    result = filter_transactions_by_date(transactions_list).to_dict()
    print(result)
    expected: dict = {"Дата операции": {}, "Сумма": {}, "Описание": {}}
    assert result == expected
