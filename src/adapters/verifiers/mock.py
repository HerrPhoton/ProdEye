from collections import deque
from collections.abc import Sequence

from src.core.dto import Detection, CheckoutRequest, VisualCheckResult
from src.core.dto import VisualCheckStatus
from src.core.mappers import visual_result_from_mapping
from src.core.services import VisualVerifier
from src.app.configs.verifiers import MockVerifierConfig


class MockVisualVerifier(VisualVerifier):
    """
    Моковый визуальный верификатор после сканирования товара.
    """

    def __init__(self, config: MockVerifierConfig):
        """
        Иницализирует моковый верификатор.

        :param config: Конфигурация мокового верификатора.
        :type config: MockVerifierConfig
        """
        self.results: deque[VisualCheckResult] = deque([
            visual_result_from_mapping(r)
            for r in config.results
        ])

    def verify(
        self,
        detections: Sequence[Detection],
        request: CheckoutRequest,
    ) -> VisualCheckResult:
        """
        Возвращает моковые результаты визуальной проверки.

        Возвращает результаты, начиная с начала списка.
        Если список результатов пуст, то возвращает результат со статусом ``pending``.

        :param detections: Объекты, обнаруженные детектором на текущем видеокадре.
        :type detections: Sequence[Detection]
        :param request: Запрос от кассы с информацией об ожидаемом товаре.
        :type request: CheckoutRequest
        :return: Моковый результат визуальной проверки товара.
        :rtype: VisualCheckResult
        """
        if self.results:
            return self.results.popleft()

        return VisualCheckResult(status=VisualCheckStatus.PENDING)
