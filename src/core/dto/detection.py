from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    """
    Детекция одного объекта на видеокадре.

    :var class_id: Числовой идентификатор класса.
    :vartype class_id: int
    :var label: Название товара.
    :vartype label: str
    :var confidence: Уверенность детекции в диапазоне ``[0.0, 1.0]``.
    :vartype confidence: float
    :var bbox: Bbox в формате ``(x1, y1, x2, y2)`` в координатах исходного кадра.
    :vartype bbox: tuple[int, int, int, int]
    """
    class_id: int
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]
