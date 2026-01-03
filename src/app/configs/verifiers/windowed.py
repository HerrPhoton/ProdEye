from typing import Any
from dataclasses import dataclass


@dataclass(frozen=True)
class WindowedVerifierConfig:
    """
    Параметры инициализации верификатора с временным окном.

    :param window_size: Длительность окна агрегации детекций (в секундах).
    :type window_size: float
    :param confidence: Минимальная уверенность детекции для подтверждения товара.
    :param detections: Минимальное число появлений класса.
    """
    window_size: float = 5.0,
    confidence: float = 0.5,
    detections: int = 1,


def parse(raw: dict[str, Any]) -> WindowedVerifierConfig:
    """
    Создает экземпляр конфигурации мокового детектора :class:`WindowedVerifierConfig`
    на основе переданного словаря.

    :param raw: Словарь с параметрами для конфигурации.
    :type raw: dict[str, Any]
    :return: Экземпляр конфигурации, инициализированный параметрами из словаря.
    :rtype: MockDetectorConfig
    """
    thresholds = raw.get("thresholds", {})
    return WindowedVerifierConfig(
        window_size=raw["window_size"],
        confidence=thresholds.get("confidence"),
        detections=thresholds.get("detections"),
    )
