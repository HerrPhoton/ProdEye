from src.core.dto import VisualCheckResult
from src.app.configs.checkout import UICheckoutOutputConfig


class UICheckoutOutput:

    def __init__(self, config: UICheckoutOutputConfig):
        self.last_result: VisualCheckResult | None = None

    def send_result(self, result: VisualCheckResult) -> None:
        self.last_result = result
