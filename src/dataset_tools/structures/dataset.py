from typing import Any
from pathlib import Path
from dataclasses import dataclass
from collections.abc import Generator

import yaml

from .split import Split
from ...utils import PathLike


@dataclass
class YOLODataset:
    root: Path
    data_yaml: Path
    num_classes: int
    class_names: dict[int, str]
    splits: dict[str, Split]

    @classmethod
    def from_yaml(cls, data_yaml: PathLike) -> 'YOLODataset':
        data_yaml = Path(data_yaml).resolve()
        root = data_yaml.parent.resolve()

        with open(data_yaml) as file:
            data = yaml.safe_load(file)

        class_names = data["names"]
        num_classes = data["nc"]

        if isinstance(class_names, list):
            class_names = dict(enumerate(class_names))

        splits: dict[str, Split] = {}
        for split_name in ("train", "val", "test"):
            if split_name not in data:
                continue

            images_path = Path(data[split_name])
            if not images_path.is_absolute():
                images_path = (root / images_path).resolve()

            labels_path = cls.get_labels_dir(images_path)
            splits[split_name] = Split(
                name=split_name,
                images_dir=images_path,
                labels_dir=labels_path,
            )

        return cls(
            root=root,
            data_yaml=data_yaml,
            num_classes=num_classes,
            class_names=class_names,
            splits=splits,
        )

    @staticmethod
    def get_labels_dir(images_dir: Path) -> Path:
        if images_dir.parts[-1] == "images":
            return images_dir.with_name("labels")
        return images_dir.parent / "labels"

    def available_splits(self) -> list[str]:
        return list(self.splits.keys())

    def get_split(self, name: str) -> Split:
        try:
            return self.splits[name]
        except KeyError:
            raise KeyError(f"Сплит {name!r} отсутствует в датасете")

    def write_data_yaml(self, output_path: PathLike | None = None) -> str:
        """Создает yaml-файл, содержащий данные из атрибутов класса.

        Если `output_path=None`, то создает/перезаписывает data.yaml по пути `self.data_yaml`.

        :param PathLike output_path: Путь до data.yaml
        :return str: Путь до созданного data.yaml
        """
        if output_path is not None:
            yaml_path = output_path
        else:
            yaml_path = self.data_yaml

        with open(yaml_path, "w") as data_yaml:
            data: dict[str, Any] = {}

            for split in self.splits.values():
                data[split.name] = str(split.images_dir)

            data["nc"] = self.num_classes
            data["names"] = self.class_names

            yaml.dump(data, data_yaml, sort_keys=False)

        return str(yaml_path)

    def iter_images(self) -> Generator[Path, None, None]:
        """Итерируется по изображениям во всех сплитах.

        :yield Generator[Path, None, None]: Путь до изображения
        """
        for split in self.splits.values():
            yield from split.iter_images()

    def iter_labels(self) -> Generator[Path, None, None]:
        """Итерируется по меткам во всех сплитах.

        :yield Generator[Path, None, None]: Путь до метки
        """
        for split in self.splits.values():
            yield from split.iter_labels()

    def iter_samples(self) -> Generator[tuple[Path, Path], None, None]:
        """Итерируется по парам изображение-метка (если оба существуют) по всем сплитам.

        :yield Generator[tuple[Path, Path], None, None]: путь до изображения, путь до метки
        """
        for split in self.splits.values():
            yield from split.iter_samples()
