from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutRequest:
    """
    Запрос от кассы на визуальную проверку товара.

    :var sku: Артикул товара.
    :vartype sku: str
    :var label: Название товара.
    :vartype label: str
    :var expected_class_id: Ожидаемый класс товара у модели детекции.
    :vartype expected_class_id: int
    """
    sku: str
    label: str
    expected_class_id: int
