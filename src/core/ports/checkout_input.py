from typing import Protocol, runtime_checkable

from src.core.dto import CheckoutRequest


@runtime_checkable
class CheckoutInput(Protocol):
    """
    Входной порт взаимодействия с кассой самообслуживания.

    Касса инициирует визуальную проверку,
    передавая данные о только что отсканированном товаре.
    """

    def get_request(self) -> CheckoutRequest:
        """
        Получает запрос на визуальную проверку.

        :return: Запрос от кассы.
        :rtype: CheckoutRequest
        """
        pass
