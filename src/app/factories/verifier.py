from typing import TypeAlias

from src.core.services import VisualVerifier
from src.app.configs.verifiers import MockVerifierConfig, WindowedVerifierConfig

VerifierConfig: TypeAlias = MockVerifierConfig | WindowedVerifierConfig

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
    if isinstance(config, MockVerifierConfig):
        from src.adapters.verifiers.mock import MockVisualVerifier
        return MockVisualVerifier(config)

    if isinstance(config, WindowedVerifierConfig):
        from src.adapters.verifiers.windowed import WindowedVisualVerifier

        if classes is None:
            raise ValueError(
                "WindowedVisualVerifier requires 'classes'"
            )
        return WindowedVisualVerifier(config, classes)

    raise TypeError(
        f"Invalid configuration type: {type(config)}. "
        f"Allowed: MockVerifierConfig, WindowedVerifierConfig."
    )
