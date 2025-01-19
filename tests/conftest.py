import pytest

expected_result = [
        {"Дата операции": "10.03.2023 12:00:00", "Категория": "Еда", "Сумма": 200},
        {"Дата операции": "20.04.2023 12:00:00", "Категория": "Еда", "Сумма": 300}
        ]


# @pytest.fixture
# def samp_transactions():
#     return expected_result = [
#         {"Дата операции": "10.03.2023 12:00:00", "Категория": "Еда", "Сумма": 200},
#         {"Дата операции": "20.04.2023 12:00:00", "Категория": "Еда", "Сумма": 300}
#         ]


@pytest.fixture
def samp_transactions():
    return expected_result
