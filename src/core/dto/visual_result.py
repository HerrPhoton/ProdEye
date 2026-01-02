from enum import Enum
from dataclasses import dataclass


class VisualCheckStatus(Enum):
    PENDING = "pending"
    MATCH = "match"
    MISMATCH = "mismatch"


@dataclass(frozen=True)
class VisualCheckResult:
    """
    Результат визуальной проверки товара.

    :var status: Текущий статус визуальной проверки отсканированного товара.
    :vartype status: VisualCheckStatus
    :var confidence: Оценка уверенности в детекции ``[0.0, 1.0]``.
    :vartype confidence: float | None, optional
    :var detected_label: Метка распознанного товара.
    :vartype detected_label: str | None, optional
    """
    status: VisualCheckStatus
    confidence: float | None = None
    detected_label: str | None = None
