from abc import ABC, abstractmethod
from collections.abc import Sequence

from ..dto import Detection, CheckoutRequest, VisualCheckResult


class VisualVerifier(ABC):
    """
    Сервис визуальной проверки соответствия товара.
    """

    @abstractmethod
    def verify(
        self,
        detections: Sequence[Detection],
        request: CheckoutRequest
    ) -> VisualCheckResult:
        """
        Выполняет визуальную проверку соответствия товара.

        Метод анализирует результаты детекции и ожидаемый товар,
        предоставленный кассой, и формирует результат визуальной проверки.

        :param detections: Объекты, обнаруженные детектором на текущем видеокадре.
        :type detections: Sequence[Detection]
        :param request: Запрос от кассы с информацией об ожидаемом товаре.
        :type request: CheckoutRequest
        :return: Результат визуальной проверки товара.
        :rtype: VisualCheckResult
        """
        raise NotImplementedError
