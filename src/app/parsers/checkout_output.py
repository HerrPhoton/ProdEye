from typing import Any

from src.app.configs.checkout import UICheckoutOutputConfig, MockCheckoutOutputConfig
from src.app.configs.checkout.outputs.ui import parse as parse_ui
from src.app.configs.checkout.outputs.mock import parse as parse_mock

CheckoutOutputConfig = MockCheckoutOutputConfig | UICheckoutOutputConfig

def parse_checkout_output(raw_data: dict[str, Any]) -> CheckoutOutputConfig:
    """
    Возвращает экземпляр конфигурации результатов для кассы в зависимости от
    типа переданной конфигурации по ключу ``"type"``.

    :param raw_data: Словарь с параметрами запросов от кассы.
    :type raw_data: dict[str, Any]
    :raises TypeError: Если тип конфигурации не соответвует допустимому.
    :return: Экземпляр конфигурации результатов для кассы.
    :rtype: CheckoutOutputConfig
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
                f"Invalid checkout output configuration type: {type}. "
                f"Allowed: mock, ui."
            )
