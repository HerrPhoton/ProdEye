from typing import Any
from dataclasses import dataclass
from collections.abc import Mapping, Iterable


@dataclass(frozen=True)
class MockCheckoutOutputConfig:
    """
    Параметры инициализации моковых результатов для кассы самообслуживания.

    :var results: Список моковых результатов для кассы, где один запрос вида
        ``{status: match | mismatch | pending, confidence: float | None, detected_label: str | None}``.
    :vartype results: Iterable[Mapping[str, Any]]
    """
    results: Iterable[Mapping[str, Any]]


def parse(raw: dict[str, Any]) -> MockCheckoutOutputConfig:
    """
    Создает экземпляр конфигурации модели моковых результатов для кассы самообслуживания
    :class:`MockCheckoutOutputConfig` на основе переданного словаря.

    :param raw: Словарь с параметрами для конфигурации.
    :type raw: dict[str, Any]
    :return: Экземпляр конфигурации, инициализированный параметрами из словаря.
    :rtype: MockCheckoutOutputConfig
    """
    return MockCheckoutOutputConfig(
        results=raw.get("results", []),
    )
