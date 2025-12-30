from src.core.dto import CheckoutRequest
from src.app.configs.checkout import MockCheckoutInputConfig


class MockCheckoutInput:

    def __init__(self, config: MockCheckoutInputConfig):
        self._iterator = iter(config.requests)

    def get_request(self) -> CheckoutRequest:
        try:
            request = next(self._iterator)
            return CheckoutRequest(**request)
        except StopIteration:
            raise RuntimeError("No more checkout requests")
