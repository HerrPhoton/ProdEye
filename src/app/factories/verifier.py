from typing import TypeAlias

from src.core.services import VisualVerifier
from src.adapters.verifiers import MockVisualVerifier, WindowedVisualVerifier
from src.app.configs.detectors import MockDetectorConfig, YOLODetectorConfig

VerifierConfig: TypeAlias = MockVisualVerifier | WindowedVisualVerifier

def build_verifier(
    config: VerifierConfig,
    classes: dict[int, str] | None = None,
) -> VisualVerifier:
    """
    Возвращает экземпляр верификатора товаров в зависимости от
    типа переданной конфигурации.

    :param config: Конфигурация верификатора.
    :type config: VerifierConfig
    :param classes: Отображение индексов классов с их названиями.
    :type classes: dict[int, str], optional
    :raises ValueError: Если конфигурация соответвует :class:`YOLODetectorConfig`,
        но не был передан аргумент ``classes``.
    :raises TypeError: Если тип конфигурации не соответвует допустимому.
    :return: Экзепляр верификатора, инициализированный конфигурацией
    :rtype: VisualVerifier
    """
    if isinstance(config, MockDetectorConfig):
        return MockVisualVerifier(config)

    if isinstance(config, YOLODetectorConfig):
        if classes is None:
            raise ValueError(
                "WindowedVisualVerifier requires 'classes'"
            )

        return WindowedVisualVerifier(config, classes)

    raise TypeError(
        f"Invalid configuration type: {type(config)}. "
        f"Allowed: MockVisualVerifier, WindowedVisualVerifier."
    )
