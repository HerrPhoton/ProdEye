from typing import Any

from src.app.configs.checkout import UICheckoutInputConfig, MockCheckoutInputConfig
from src.app.configs.checkout.inputs.ui import parse as parse_ui
from src.app.configs.checkout.inputs.mock import parse as parse_mock

CheckoutInputConfig = MockCheckoutInputConfig | UICheckoutInputConfig

def parse_checkout_input(raw_data: dict[str, Any]) -> CheckoutInputConfig:
    """
    Возвращает экземпляр конфигурации запросов от кассы в зависимости от
    типа переданной конфигурации по ключу ``"type"``.

    :param raw_data: Словарь с параметрами запросов от кассы.
    :type raw_data: dict[str, Any]
    :raises TypeError: Если тип конфигурации не соответвует допустимому.
    :return: Экземпляр конфигурации запросов от кассы.
    :rtype: CheckoutInputConfig
    """
    data_copy = raw_data.copy()
    type = data_copy.pop("type")

    match type:
        case "ui":
            return parse_ui(data_copy)

        case "mock":
            return parse_mock(data_copy)

        case _:
            raise TypeError(
                f"Invalid checkout input configuration type: {type}. "
                f"Allowed: mock, ui."
            )
