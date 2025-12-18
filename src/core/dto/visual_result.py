from dataclasses import dataclass


@dataclass(frozen=True)
class VisualCheckResult:
    """
    Результат визуальной проверки товара.

    :var is_match: Соответсвует ли распознанный товар отсканированному.
    :vartype is_match: bool
    :var confidence: Оценка уверенности в детекции ``[0.0, 1.0]``.
    :vartype confidence: float
    :var detected_label: Метка распознанного товара.
    :vartype detected_label: str | None
    """
    is_match: bool
    confidence: float
    detected_label: str | None
