from typing import TypeAlias

from src.core.ports import CheckoutInput
from src.app.configs.checkout import UICheckoutInputConfig, MockCheckoutInputConfig

CheckoutInputConfig: TypeAlias = MockCheckoutInputConfig | UICheckoutInputConfig

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
        from src.adapters.checkout.inputs.mock import MockCheckoutInput
        return MockCheckoutInput(config)

    if isinstance(config, UICheckoutInputConfig):
        from src.adapters.checkout.inputs.ui import UICheckoutInput
        return UICheckoutInput(config)

    raise TypeError(
        f"Invalid configuration type: {type(config)}. "
        f"Allowed: MockCheckoutInputConfig, UICheckoutInputConfig."
    )
