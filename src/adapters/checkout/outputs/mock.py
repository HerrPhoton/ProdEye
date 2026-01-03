from src.core.dto import VisualCheckResult
from src.core.mappers import visual_result_from_mapping
from src.app.configs.checkout import MockCheckoutOutputConfig


class MockCheckoutOutput:

    def __init__(self, config: MockCheckoutOutputConfig):
        self.results: list[VisualCheckResult] = [
            visual_result_from_mapping(r)
            for r in config.results
        ]

    def send_result(self, result: VisualCheckResult) -> None:
        """
        Добавляет новый результат проверки для кассы в буфер.

        :param result: Результат проверки отсканированного товара.
        :type result: VisualCheckResult
        """
        self.results.append(result)
