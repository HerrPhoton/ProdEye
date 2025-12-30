from typing import TypeAlias

from src.core.ports import CheckoutInput
from src.adapters.checkout import UICheckoutInput, MockCheckoutInput
from src.app.configs.checkout import UICheckoutInputConfig, MockCheckoutInputConfig

CheckoutInputConfig: TypeAlias = MockCheckoutInput | UICheckoutInput

def build_checkout_input(config: CheckoutInputConfig) -> CheckoutInput:
    """
    Возвращает экземпляр модели запросов от кассы в зависимости от
    типа переданной конфигурации.

    :param config: Конфигурация модели запросов от кассы.
    :type config: CheckoutInputConfig
    :raises TypeError: Если тип конфигурции не соответвует допустимому.
    :return: Экзепляр модели запросов от кассы, инициализированный конфигурацией.
    :rtype: CheckoutInput
    """
    if isinstance(config, MockCheckoutInputConfig):
        return MockCheckoutInput(config)

    if isinstance(config, UICheckoutInputConfig):
        return UICheckoutInput(config)

    raise TypeError(
        f"Invalid configuration type: {type(config)}. "
        f"Allowed: MockCheckoutInputConfig, UICheckoutInputConfig."
    )
