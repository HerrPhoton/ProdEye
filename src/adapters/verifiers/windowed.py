import time
from collections import deque, defaultdict
from dataclasses import dataclass
from collections.abc import Sequence

from src.core.dto import Detection, CheckoutRequest, VisualCheckResult
from src.core.dto import VisualCheckStatus
from src.core.services import VisualVerifier
from src.app.configs.verifiers import WindowedVerifierConfig


@dataclass
class TimedDetections:
    """
    Список детекций товаров в определенный временной шаг.

    :var timestamp: Временной шаг, в который были сделаны детекции.
    :vartype timestamp: float
    :var detections: Список детекций товаров.
    :vartype detections: list[Detection]
    """
    timestamp: float
    detections: list[Detection]


@dataclass
class ClassStats:
    """
    Статистика детекций по определенному классу.

    :var count: Количество детекций класса.
    :vartype count: int
    :var mean_confidence: Средняя уверенность детекций класса.
    :vartype mean_confidence: float
    """
    count: int
    mean_confidence: float


class WindowedVisualVerifier(VisualVerifier):
    """
    Визуальный верификатор с временным окном после сканирования товара.
    """

    def __init__(self, config: WindowedVerifierConfig, classes: dict[int, str]):
        """
        Иницализирует верификатор с временным окном.

        :param config: Конфигурация верификатора с временным окном.
        :type config: WindowedVerifierConfig
        :param classes: Отображение индексов классов с их названиями.
        :type classes: dict[int, str]
        """
        self.window_size = config.window_size
        self.conf_threshold = config.confidence
        self.detections_threshold = config.detections
        self.classes = classes

        self._buffer: deque[TimedDetections] = deque()
        self._active_request: CheckoutRequest | None = None
        self._request_start_ts: float | None = None

    def verify(
        self,
        detections: Sequence[Detection],
        request: CheckoutRequest,
    ) -> VisualCheckResult:
        """
        Выполняет визуальную проверку соответствия товара с учетом временного окна.

        Наполняет буфер детекциями с кадров в течение указанного временного промежутка.
        Если заданное временное окно не было пройдено, то возвращает статус ``pending``.

        Оценка соответствия отсканированного товара происходит на основе класса, который
        в течение заданного временного окна появлялся большее количество раз и у которого
        средняя уверенность в детекции максимальная.

        :param detections: Объекты, обнаруженные детектором на текущем видеокадре.
        :type detections: Sequence[Detection]
        :param request: Запрос от кассы с информацией об ожидаемом товаре.
        :type request: CheckoutRequest
        :return: Результат визуальной проверки товара.
        :rtype: VisualCheckResult
        """
        now = time.time()

        # Начать новую сессию при новом запросе от кассы
        if self._is_new_request(request):
            self._start_new_session(request, now)

        # Добавить детекции текущего кадра
        self._buffer.append(
            TimedDetections(
                timestamp=now,
                detections=list(detections),
            )
        )

        # Очистка истекших детекций
        self._drop_expired(now)

        # Проверка на прохождение заданного временного окна
        if not self._window_elapsed(now):
            return VisualCheckResult(status=VisualCheckStatus.PENDING)

        # Агрегация детекций во временном окне
        stats = self._aggregate()
        if not stats:
            return VisualCheckResult(status=VisualCheckStatus.MISMATCH)

        best_class_id, best_stats = self._select_best_stats(stats)
        detected_label = self.classes.get(best_class_id)

        if detected_label == request.label:
            status = VisualCheckStatus.MATCH
        else:
            status = VisualCheckStatus.MISMATCH

        return VisualCheckResult(
            status=status,
            confidence=best_stats.mean_confidence,
            detected_label=detected_label,
        )

    def _is_new_request(self, request: CheckoutRequest) -> bool:
        """
        Проверяет, является ли запрос новым.

        :param request: Запрос для проверки.
        :type request: CheckoutRequest
        :return: ``True``, если запрос новый; ``False`` - иначе.
        :rtype: bool
        """
        return self._active_request != request

    def _start_new_session(self, request: CheckoutRequest, now: float) -> None:
        """
        Инициализирует новую сесиию при новом запросе.
        Очищает буфер детекций от прошлых запросов.

        :param request: Новый запрос.
        :type request: CheckoutRequest
        :param now: Временной шаг запроса.
        :type now: float
        """
        self._active_request = request
        self._request_start_ts = now
        self._buffer.clear()

    def _window_elapsed(self, now: float) -> bool:
        """
        Проверяет, прошло ли временное окно запроса.

        :param now: Текущий временной шаг.
        :type now: float
        :raises ValueError: Если не задано начальное время запроса :attr:`_request_start_ts`.
        :return: ``True``, если прошло времени больше, чем :attr:`window_size`; ``False`` - иначе.
        :rtype: bool
        """
        if self._request_start_ts is None:
            raise ValueError(
                "The initial time of the _request_start_ts request is not set."
            )

        return (now - self._request_start_ts) >= self.window_size

    def _drop_expired(self, now: float) -> None:
        """
        Удаляет из буфера детекции, находящиеся за пределом временного окна.

        :param now: Текущий временной шаг.
        :type now: float
        """
        while self._buffer:
            if now - self._buffer[0].timestamp > self.window_size:
                self._buffer.popleft()
            else:
                break

    def _aggregate(self) -> dict[int, ClassStats]:
        """
        Агрегирует информация по всем детекциям во временном окне.

        :return: Словарь вида ``{class_id: ClassStats}``.
        :rtype: dict[int, ClassStats]
        """
        confidences: dict[int, list[float]] = defaultdict(list)
        for frame in self._buffer:
            for det in frame.detections:
                if det.confidence >= self.conf_threshold:
                    confidences[det.class_id].append(det.confidence)

        stats: dict[int, ClassStats] = {}
        for class_id, confidences in confidences.items():
            if len(confidences) >= self.detections_threshold:
                stats[class_id] = ClassStats(
                    count=len(confidences),
                    mean_confidence=sum(confidences) / len(confidences),
                )

        return stats

    def _select_best_stats(
        self,
        stats: dict[int, ClassStats],
    ) -> tuple[int, ClassStats]:
        """
        Возвращает статистику класса, у которого максимальное
        количество появлений ``count`` и максимальная средняя
        уверенность детекций ``mean_confidence``.

        :param stats: _description_
        :type stats: dict[int, ClassStats]
        :return: _description_
        :rtype: tuple[int, ClassStats]
        """
        return max(
            stats.items(),
            key=lambda item: (item[1].count, item[1].mean_confidence),
        )
