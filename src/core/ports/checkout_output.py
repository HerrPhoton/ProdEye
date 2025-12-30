from typing import Protocol, runtime_checkable

from src.core.dto import VisualCheckResult


@runtime_checkable
class CheckoutOutput(Protocol):
    """
    Выходной порт передачи результата визуальной проверки в кассу.
    """

    def send_result(self, result: VisualCheckResult) -> None:
        """
        Отправляет результат визуальной проверки в кассу.

        :param result: Результат проверки.
        :rtype: VisualCheckResult
        """
        pass
