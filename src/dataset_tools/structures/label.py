from pathlib import Path
from dataclasses import field, dataclass

from .bbox import BBox
from ...utils import PathLike


@dataclass
class YOLOLabel:
    """Представляет файл метки YOLO с bbox'ами."""
    path: PathLike
    bboxes: list[BBox] = field(default_factory=list)

    def __post_init__(self):
        """Считывает bbox'ы из файла после создания объекта."""
        self.path = Path(self.path)
        self.bboxes = self.read()

    def read(self) -> list[BBox]:
        """Возвращает список значений bbox'ов в файле.

        :raises ValueError: При неверном количестве значений bbox'ов
        :return list[BBox]: Список bbox'ов (class_id, x, y, w, h)
        """
        bboxes: list[BBox] = []
        with open(self.path) as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                values = line.split()
                if len(values) == 5:
                    class_id = int(float(values[0]))
                    x, y, w, h = map(float, values[1:])
                    bboxes.append(BBox(class_id, x, y, w, h))
                else:
                    raise ValueError("Неверное количество значений bbox")

        return bboxes

    def write(self) -> None:
        """Перезаписывает файл метки текущими значениям bbox'ов."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as file:
            data = [f"{b.class_id} {b.x} {b.y} {b.w} {b.h}\n" for b in self.bboxes]
            file.writelines(data)

    def validate(self, num_classes: int) -> bool:
        """Проверяет корректность всех bbox'ов в метке.

        :param int num_classes: Количество классов в датасете (классы: 0..num_classes-1)
        :return bool: Являются ли все значения bbox в метке допустимыми
        """
        return all(b.validate(num_classes) for b in self.bboxes)

    def is_empty(self) -> bool:
        """Проверяет, является ли метка пустой.

        :return bool: True, если метка пустая; False - иначе
        """
        return len(self.bboxes) == 0
