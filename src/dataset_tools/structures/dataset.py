from pathlib import Path
from dataclasses import field, dataclass
from collections.abc import Generator

import yaml

from .split import Split
from ...utils import PathLike


@dataclass
class YOLODataset:
    root: Path
    splits: dict[str, Split] = field(default_factory=dict)
    num_classes: int | None = None
    class_names: list[str] | None = None

    @classmethod
    def from_yaml(cls, data_yaml: PathLike) -> 'YOLODataset':
        data_yaml = Path(data_yaml).resolve()
        root = data_yaml.parent.resolve()

        with open(data_yaml) as file:
            data = yaml.safe_load(file)

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
            splits=splits,
            num_classes=data.get("nc"),
            class_names=data.get("names"),
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
