from typing import Any
from collections.abc import Mapping, Iterable

from src.core.dto import VisualCheckResult, VisualCheckStatus
from src.app.configs.checkout import MockCheckoutOutputConfig


class MockCheckoutOutput:

    def __init__(self, config: MockCheckoutOutputConfig):
        self.results = self._parse_results(config.results)

    def send_result(self, result: VisualCheckResult) -> None:
        """
        Добавляет новый результат проверки для кассы в буфер.

        :param result: Результат проверки отсканированного товара.
        :type result: VisualCheckResult
        """
        self.results.append(result)

    def _parse_results(
        self,
        raw_results: Iterable[Mapping[str, Any]],
    ) -> list[VisualCheckResult]:
        """
        Преобразует отображения моковых результатов в список объектов
        класса :class:`VisualCheckResult`.

        :param raw_results: Отображения с моковыми результатами.
        :type raw_results: Iterable[Mapping[str, Any]]
        :return: Список результатов для кассы с объектами :class:`VisualCheckResult`.
        :rtype: list[VisualCheckResult]
        """
        results: list[VisualCheckResult] = []
        for raw in raw_results:
            status_raw = raw["status"]
            status = VisualCheckStatus(status_raw)

            results.append(
                VisualCheckResult(
                    status=status,
                    confidence=raw.get("confidence"),
                    detected_label=raw.get("detected_label"),
                )
            )

        return results
