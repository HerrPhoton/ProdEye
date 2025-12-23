from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutRequest:
    """
    Запрос от кассы на визуальную проверку товара.

    :var sku: Артикул товара.
    :vartype sku: str
    :var label: Название товара.
    :vartype label: str
    """
    sku: str
    label: str
