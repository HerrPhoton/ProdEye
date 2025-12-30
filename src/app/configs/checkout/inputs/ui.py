from typing import Any
from dataclasses import dataclass


@dataclass(frozen=True)
class UICheckoutInputConfig:
    """
    Параметры инициализации запросов от UI-кассы самообслуживания.
    """
    pass


def parse(raw: dict[str, Any]) -> UICheckoutInputConfig:
    """
    Создает экземпляр конфигурации модели запросов от UI-кассы самообслуживания
    :class:`UICheckoutInputConfig` на основе переданного словаря.

    :param raw: Словарь с параметрами для конфигурации.
    :type raw: dict[str, Any]
    :return: Экземпляр конфигурации, инициализированный параметрами из словаря.
    :rtype: UICheckoutInputConfig
    """
    return UICheckoutInputConfig()
