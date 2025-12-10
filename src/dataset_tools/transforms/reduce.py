import random
from typing import Literal
from pathlib import Path
from dataclasses import dataclass
from collections.abc import Iterable

from natsort import natsorted

from ...utils import PathLike, normalize_to_paths
from ..structures import Split, YOLODataset


@dataclass
class ReductionResult:
    """Результат уменьшения размера одного сплита.

    :param int initial_count: Количество сэмплов в сплите до удаления
    :param int removed_count: Сколько сэмплов было удалено
    :param int final_count: Количество сэмплов, оставшихся после удаления
    :param list[tuple[Path, Path]] removed_files: Список удалённых сэмплов (изображение, метка)
    """
    initial_count: int
    removed_count: int
    final_count: int
    removed_files: list[tuple[Path, Path]]


class DatasetReducer:

    def __init__(self, split_dir: PathLike | Iterable[PathLike]):
        """Инициализирует сплиты датасета для уменьшения их размера.
        На основе переданных путей создает экземпляры Split. В качестве названий сплитов
        использует имена директорий `split_dir`.

        :param PathLike | Iterable[PathLike] split_dir: Путь/пути до директорий сплитов датасета
        """
        self.splits: dict[str, Split] = {
            Path(d).name: Split.from_dir(d) for d in normalize_to_paths(split_dir)
        }

    @classmethod
    def from_splits(cls, splits: Iterable[Split]) -> 'DatasetReducer':
        """Создает экземпляр DatasetReducer из экземляров Split.

        :param Iterable[Split] splits: Экземпляры сплитов датасета
        :return DatasetReducer: Экзмепляр DatasetReducer, содержащий переданные сплиты
        """
        reducer = cls.__new__(cls)
        reducer.splits = {
            Path(split.images_dir).name: split for split in splits
        }
        return reducer

    @classmethod
    def from_dataset(cls, dataset: YOLODataset) -> 'DatasetReducer':
        """Создает экземпляр DatasetReducer из экземляра YOLODataset.

        :param YOLODataset dataset: Объект датасета YOLODataset
        :return DatasetReducer: Экзмепляр DatasetReducer, содержащий сплиты из датасета
        """
        reducer = cls.__new__(cls)
        reducer.splits = dataset.splits
        return reducer

    def reduce(
        self,
        split_sizes: dict[str, int],
        strategy: Literal["first", "last", "random"] = "random",
    ) -> dict[str, ReductionResult]:
        """Уменьшает размер сплитов путем удаления сэмплов с заданной стратегий отбора.

        Если сплит содержит меньше сэмплов, чем указано в `split_sizes`,
        то он остаётся без изменений.

        Порядок элементов определяется естественной сортировкой (natural sort) имён файлов,
        тогда стратегия выбора:
          - "first" - удаляет первые имена в естественном порядке;
          - "last"  - удаляет последние имена в естественном порядке;
          - "random" - удаляет случайный набор сэмплов.

        :param dict[str, int] split_sizes: Целевые размеры отдельно для указанных сплитов.
                                           Ключи - названия сплитов, значения - целевые размеры
        :param Literal["first", "last", "random"] strategy: Стратегия выбора удаляемых сэмплов
        :param dict[str, str] | None filter: Дополнительный фильтр имен сэмплов.
        :return dict[str, ReductionResult]: Словарь с названиями сплитов и с информацией об удаленных сэмплах.
        """
        results: dict[str, ReductionResult] = {}
        for split_name, size in split_sizes.items():
            results[split_name] = self._reduce_split(
                split=self.splits[split_name],
                size=size,
                strategy=strategy,
            )

        return results

    def _reduce_split(
        self,
        split: Split,
        size: int,
        strategy: Literal["first", "last", "random"] = "random",
    ) -> ReductionResult:
        """Удаляет сэмплы из сплита с заданной стратегий отбора.

        :param Split split: Экземпляр сплита, в котором будут удалены сэмплы
        :param int size: Целевое количество сэмплов в сплите
        :param Literal["first", "last", "random"] strategy: Стратегия выбора удаляемых сэмплов
        :return ReductionResult: Информация об удаленных сэмплах
        """
        # Сортировка сэмплов в естественном порядке
        samples = natsorted(split.iter_samples())

        # Формирование списка сэмплов для удаления с
        # выбранной стратегией
        remove_count = max(0, len(samples) - size)
        match strategy:
            case "first":
                samples_to_remove = samples[:remove_count]

            case "last":
                samples_to_remove = samples[-remove_count:]

            case "random":
                samples_to_remove = random.sample(samples, k=remove_count)

        # Удаление выбранных сэмплов
        removed: list[tuple[Path, Path]] = []
        for image_path, label_path in samples_to_remove:
            try:
                image_path.unlink()
                label_path.unlink()
                removed.append((image_path, label_path))
            except:
                continue

        return ReductionResult(
            initial_count=len(samples),
            removed_count=len(removed),
            final_count=split.count_samples(),
            removed_files=removed
        )
