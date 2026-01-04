from typing import TypeAlias

from src.core.ports import CheckoutOutput
from src.app.configs.checkout import UICheckoutOutputConfig, MockCheckoutOutputConfig

CheckoutOutputConfig: TypeAlias = MockCheckoutOutputConfig | UICheckoutOutputConfig

def build_checkout_output(config: CheckoutOutputConfig) -> CheckoutOutput:
    """
    Возвращает экземпляр модели результатов для кассы в зависимости от
    типа переданной конфигурации.

    :param config: Конфигурация модели результатов для кассы.
    :type config: CheckoutOutputConfig
    :raises TypeError: Если тип конфигурции не соответвует допустимому.
    :return: Экзепляр модели результатов для, инициализированный конфигурацией.
    :rtype: CheckoutOutput
    """
    if isinstance(config, MockCheckoutOutputConfig):
        from src.adapters.checkout.outputs.mock import MockCheckoutOutput
        return MockCheckoutOutput(config)

    if isinstance(config, UICheckoutOutputConfig):
        from src.adapters.checkout.outputs.ui import UICheckoutOutput
        return UICheckoutOutput(config)

    raise TypeError(
        f"Invalid configuration type: {type(config)}. "
        f"Allowed: MockCheckoutOutputConfig, UICheckoutOutputConfig."
    )
