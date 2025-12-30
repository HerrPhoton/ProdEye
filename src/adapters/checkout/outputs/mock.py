from src.core.dto import VisualCheckResult
from src.app.configs.checkout import MockCheckoutOutputConfig


class MockCheckoutOutput:

    def __init__(self, config: MockCheckoutOutputConfig):
        results = [VisualCheckResult(**result) for result in config.results]
        self.results: list[VisualCheckResult] = results

    def send_result(self, result: VisualCheckResult) -> None:
        self.results.append(result)
