from abc import ABC, abstractmethod


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
    def run_once(self) -> None:
        """Выполняет один цикл визуальной проверки."""
        raise NotImplementedError
