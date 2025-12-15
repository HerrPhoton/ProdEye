from collections.abc import Mapping, Iterable

from .path import PathHandler
from ...utils import LABEL_EXTENSIONS, PathLike
from ..structures import BBox, YOLOLabel


class YOLOLabelHandler(PathHandler):

    def __init__(
        self,
        labels_dir: PathLike | Iterable[PathLike],
        label_ext: Iterable[str] = LABEL_EXTENSIONS,
        recursive: bool = False,
    ):
        """
        Инициализация менеджера для работы с метками YOLO.

        :param labels_dir: Путь/пути до директории с метками.
        :type labels_dir: PathLike | Iterable[PathLike]
        :param label_ext: Расширения файлов с метками.
        :type label_ext: Iterable[str], optional
        :param recursive: Искать ли метки в поддиректориях ``labels_dir``.
        :type recursive: bool, optional
        :raises ValueError: Если указанная директория/директории в ``labels_dir`` не найдена.
        """
        super().__init__(labels_dir, label_ext, recursive)

    def get_background_ratio(self) -> float:
        """
        Возвращает долю background-изображений в :attr:``images_dir``.

        :return: Доля background-изображений (0-1).
        :rtype: float
        """
        total_count = 0
        background_count = 0

        for label_path in self.iter_files():
            total_count += 1

            label = YOLOLabel(label_path)
            if label.is_empty():
                background_count += 1

        return background_count / total_count if total_count > 0 else 0

    def validate_labels(self, num_classes: int) -> list[str]:
        """
        Проверяет все метки в :attr:`labels_dir` на корректность.

        Для каждого bbox должны выполняться условия:
        1) Номер класса должен быть в диапазоне ``0..num_classes-1``
        2) Координаты и размеры bbox должны быть в диапазоне ``[0, 1]``

        :param num_classes: Количество классов в датасете.
        :type num_classes: int
        :return: Список файлов, которые содержат некорректные значения
        :rtype: list[str]
        """
        incorrect: list[str] = []
        for label_path in self.iter_files():
            try:
                label = YOLOLabel(label_path)
                if not label.validate(num_classes):
                    incorrect.append(str(label_path))
            except:
                incorrect.append(str(label_path))

        return incorrect

    def set_classes(self, new_classes: Mapping[int, int]) -> list[str]:
        """
        Устанавливает для каждого bbox в метках :attr:`labels_dir` указанный класс.

        :param new_classes: Отображение индексов классов для замены.
        :type new_classes: Mapping[int, int]
        :return: Список файлов, в которых были заменены классы.
        :rtype: list[str]
        """
        changed_files: list[str] = []
        for label_path in self.iter_files():
            label = YOLOLabel(label_path)

            original_ids = [b.class_id for b in label.bboxes]
            label.bboxes = [BBox(new_classes.get(b.class_id, b.class_id), b.x, b.y, b.w, b.h) for b in label.bboxes]

            new_ids = [b.class_id for b in label.bboxes]
            if original_ids != new_ids:
                label.write()
                changed_files.append(str(label_path))

        return changed_files

    def remove_classes(self, classes: Iterable[int]) -> list[str]:
        """
        Удаляет bbox'ы в метках :attr:`labels_dir` с указанными классами.

        :param classes: Индексы классов для удаления.
        :type classes: Iterable[int]
        :return: Список файлов, в которых были удалены bbox'ы.
        :rtype: list[str]
        """
        changed_files: list[str] = []
        for label_path in self.iter_files():
            label = YOLOLabel(label_path)

            original_count = len(label.bboxes)
            label.bboxes = [
                b for b in label.bboxes
                if not b.class_id in classes
            ]

            if original_count != len(label.bboxes):
                label.write()
                changed_files.append(str(label_path))

        return changed_files

    def remove_invalid_bboxes(self, num_classes: int) -> list[str]:
        """
        Удаляет некорректные bbox'ы из меток в :attr:`labels_dir`.

        Оставляет только валидные bbox'ы в файлах:
        1) Номер класса должен быть в диапазоне ``0..num_classes-1``
        2) Координаты и размеры bbox должны быть в диапазоне ``[0, 1]``

        :param num_classes: Количество классов в датасете.
        :type num_classes: int
        :return: Список файлов, из которых были удалены невалидные bbox'ы.
        :rtype: list[str]
        """
        changed_files: list[str] = []
        for label_path in self.iter_files():
            label = YOLOLabel(label_path)

            original_count = len(label.bboxes)
            label.bboxes = [
                b for b in label.bboxes
                if b.validate(num_classes)
            ]

            if original_count != len(label.bboxes):
                label.write()
                changed_files.append(str(label_path))

        return changed_files

    def remove_files_with_invalid_bboxes(self, num_classes: int) -> list[str]:
        """
        Удаляет файлы меток с невалидными bbox'ами из :attr:`labels_dir`.

        :param num_classes: Количество классов в датасете.
        :type num_classes: int
        :return: Список удаленных файлов меток.
        :rtype: list[str]
        """
        removed_files: list[str] = []
        for label_path in self.iter_files():
            label = YOLOLabel(label_path)
            if not all(b.validate(num_classes) for b in label.bboxes):
                label_path.unlink()
                removed_files.append(str(label_path))

        return removed_files

    def rename_labels(self, new_name: str, start_idx: int = 0, zero_padding: int = 0) -> list[tuple[str, str]]:
        """
        Переименовывает метки по паттерну ``new_name_{idx}``.

        :param new_name: Базовое имя для новых файлов (префикс).
        :type new_name: str
        :param start_idx: Начальный индекс.
        :type start_idx: int, optional
        :param zero_padding: Количество нулей для паддинга индекса.
        :type zero_padding: int, optional
        :return: Список переименованных меток ``(старое название, новое название)``.
        :rtype: list[tuple[str, str]]
        """
        renamed: list[tuple[str, str]] = []
        idx = start_idx

        for label_path in self.iter_files():
            # Паддинг индекса
            idx_str = str(idx).zfill(zero_padding)

            # Новое имя для метки
            new_label_name = f"{new_name}_{idx_str}{label_path.suffix}"
            new_label_path = label_path.parent / new_label_name

            # Переименовываем метку
            label_path.rename(new_label_path)

            renamed.append((str(label_path), str(new_label_path)))
            idx += 1

        return renamed
