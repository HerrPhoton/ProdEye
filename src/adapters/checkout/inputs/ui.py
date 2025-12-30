from queue import Queue

from src.core.dto import CheckoutRequest
from src.app.configs.checkout import UICheckoutInputConfig


class UICheckoutInput:

    def __init__(self, config: UICheckoutInputConfig):
        self._queue: Queue[CheckoutRequest] = Queue()

    def put(self, request: CheckoutRequest) -> None:
        self._queue.put(request)

    def get_request(self) -> CheckoutRequest:
        return self._queue.get()
