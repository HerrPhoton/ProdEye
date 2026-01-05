from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from src.core.dto import Detection, VisualCheckResult


@dataclass(frozen=True)
class PipelineStepResult:
    frame: np.ndarray
    detections: list[Detection]
    result: VisualCheckResult


class Pipeline(ABC):
    """
    Контракт пайплайна визуальной проверки товара.

    Отвечает за:
    - получение запроса от кассы
    - получение видеокадра
    - запуск детекции
    - передачу результата обратно кассе
    """

    @abstractmethod
    def run_once(self) -> PipelineStepResult:
        """
        Выполняет один цикл визуальной проверки.

        :return: Результат одного шага пайплайна.
        :rtype: PipelineStepResult
        """
        raise NotImplementedError
