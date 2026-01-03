from typing import Any
from dataclasses import dataclass
from collections.abc import Mapping, Iterable


@dataclass(frozen=True)
class MockVerifierConfig:
    """
    Параметры инициализации мокового верификатора.

    :var results: Список моковых результатов для кассы, где один запрос вида
    ``{status: match | mismatch | pending, confidence: float | None, detected_label: str | None}``.
    :vartype results: Iterable[Mapping[str, Any]]
    """
    results: Iterable[Mapping[str, Any]]


def parse(raw: dict[str, Any]) -> MockVerifierConfig:
    """
    Создает экземпляр конфигурации мокового детектора :class:`MockVerifierConfig`
    на основе переданного словаря.

    :param raw: Словарь с параметрами для конфигурации.
    :type raw: dict[str, Any]
    :return: Экземпляр конфигурации, инициализированный параметрами из словаря.
    :rtype: MockDetectorConfig
    """
    return MockVerifierConfig(
        results=raw.get("results", []),
    )
