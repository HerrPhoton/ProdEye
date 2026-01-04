from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutRequest:
    """
    Запрос от кассы на визуальную проверку товара.

    :var label: Название товара.
    :vartype label: str
    :var timestamp: Временной шаг запроса.
    :vartype timestamp: float
    """
    label: str
    timestamp: float
