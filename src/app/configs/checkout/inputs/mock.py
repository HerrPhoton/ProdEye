from typing import Any
from dataclasses import dataclass
from collections.abc import Mapping, Iterable


@dataclass(frozen=True)
class MockCheckoutInputConfig:
    """
    Параметры инициализации моковых запросов от кассы самообслуживания.

    :var requests: Список моковых запросов от кассы,
        где один запрос вида ``{sku: str, label: str}``.
    :vartype requests: Iterable[Mapping[str, str]]
    """
    requests: Iterable[Mapping[str, str]]


def parse(raw: dict[str, Any]) -> MockCheckoutInputConfig:
    """
    Создает экземпляр конфигурации модели моковых запросов от кассы самообслуживания
    :class:`MockCheckoutInputConfig` на основе переданного словаря.

    :param raw: Словарь с параметрами для конфигурации.
    :type raw: dict[str, Any]
    :return: Экземпляр конфигурации, инициализированный параметрами из словаря.
    :rtype: MockCheckoutInputConfig
    """
    return MockCheckoutInputConfig(
        requests=raw.get("requests", []),
    )
