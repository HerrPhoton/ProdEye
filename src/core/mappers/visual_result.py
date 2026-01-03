from typing import Any
from collections.abc import Mapping

from src.core.dto import VisualCheckResult, VisualCheckStatus


def visual_result_from_mapping(raw: Mapping[str, Any]) -> VisualCheckResult:
    """
    Создаёт модель результата визуальной проверки
    :class:`VisualCheckResult` из отображения.

    :param raw: Отображение названий атрибутов :class:`VisualCheckResult`.
    :type raw: Mapping[str, Any]
    :raises ValueError: Если ``raw`` не содержит поля ``status``.
    :return: Экземпляр :class:`VisualCheckResult` со значениями из ``raw``.
    :rtype: VisualCheckResult
    """
    if "status" not in raw:
        raise ValueError("VisualCheckResult requires 'status' field")

    status = VisualCheckStatus(raw["status"])
    confidence = raw.get("confidence")
    detected_label = raw.get("detected_label")

    return VisualCheckResult(
        status=status,
        confidence=confidence,
        detected_label=detected_label,
    )
