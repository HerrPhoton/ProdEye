from typing import Any
from dataclasses import dataclass


@dataclass(frozen=True)
class UICheckoutOutputConfig:
    """
    Параметры инициализации результатов для UI-кассы самообслуживания.
    """
    pass


def parse(raw: dict[str, Any]) -> UICheckoutOutputConfig:
    """
    Создает экземпляр конфигурации модели результатов для UI-кассы самообслуживания
    :class:`UICheckoutOutputConfig` на основе переданного словаря.

    :param raw: Словарь с параметрами для конфигурации.
    :type raw: dict[str, Any]
    :return: Экземпляр конфигурации, инициализированный параметрами из словаря.
    :rtype: UICheckoutOutputConfig
    """
    return UICheckoutOutputConfig()
