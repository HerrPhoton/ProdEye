from typing import Any

from src.app.configs.verifiers import MockVerifierConfig, WindowedVerifierConfig
from src.app.configs.verifiers.mock import parse as parse_mock
from src.app.configs.verifiers.windowed import parse as parse_windowed

VerifierConfig = MockVerifierConfig | WindowedVerifierConfig

def parse_verifier(raw_data: dict[str, Any]) -> VerifierConfig:
    """
    Возвращает экземпляр конфигурации верификатора товаров в зависимости от
    типа переданной конфигурации по ключу ``"type"``.

    :param raw_data: Словарь с параметрами верификатора.
    :type raw_data: dict[str, Any]
    :raises TypeError: Если тип конфигурации не соответвует допустимому.
    :return: Экземпляр конфигурации верификатор.
    :rtype: VerifierConfig
    """
    data_copy = raw_data.copy()
    type = data_copy.pop("type")

    match type:
        case "windowed":
            return parse_windowed(data_copy)

        case "mock":
            return parse_mock(data_copy)

        case _:
            raise TypeError(
                f"Invalid camera configuration type: {type}. "
                f"Allowed: mock, opencv."
            )
