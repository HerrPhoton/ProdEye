from pathlib import Path
from dataclasses import field, dataclass
from collections.abc import Generator

import yaml

from src.utils import PathLike

from .split import Split


@dataclass
class YOLODataset:
    root: Path
    data_yaml: Path | None
    splits: dict[str, Split] = field(default_factory=dict)
    num_classes: int | None = None
    class_names: list[str] | None = None

    @classmethod
    def from_yaml(cls, data_yaml: PathLike) -> 'YOLODataset':
        data_yaml = Path(data_yaml).resolve()

        with open(data_yaml, encoding="utf-8") as file:
            data = yaml.safe_load(file)

        root = data_yaml.parent.resolve()
        split_defs = {}
        for split_name in ("train", "val", "test"):
            if split_name not in data:
                continue

            images_path = Path(data[split_name])
            if not images_path.is_absolute():
                images_path = (root / images_path).resolve()

            labels_path = cls._derive_labels_dir(images_path)
            split_defs[split_name] = Split(
                name=split_name,
                images_dir=images_path,
                labels_dir=labels_path,
            )

        return cls(
            root=root,
            data_yaml=data_yaml,
            splits=split_defs,
            num_classes=data.get("nc"),
            class_names=data.get("names"),
        )

    @classmethod
    def from_dirs(
        cls,
        images_dir: PathLike,
        labels_dir: PathLike,
        root: PathLike | None = None,
    ) -> 'YOLODataset':

        images = Path(images_dir).resolve()
        labels = Path(labels_dir).resolve()
        root = Path(root).resolve() if root else images.parent
        split = Split(name="default", images_dir=images, labels_dir=labels)

        return cls(
            root=root,
            data_yaml=None,
            splits={"default": split}
        )

    @staticmethod
    def _derive_labels_dir(images_dir: Path) -> Path:
        if images_dir.parts[-1] == "images":
            return images_dir.with_name("labels")
        return images_dir.parent / "labels"

    def get_split(self, name: str) -> Split:
        try:
            return self.splits[name]
        except KeyError:
            raise KeyError(f"Сплит {name!r} отсутствует в датасете")

    def available_splits(self) -> list[str]:
        return list(self.splits.keys())

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

    def iter_items(self) -> Generator[tuple[Path, Path], None, None]:
        """Итерируется по парам изображение-метка (если оба существуют) по всем сплитам.

        :yield Generator[tuple[Path, Path], None, None]: путь до изображения, путь до метки
        """
        for split in self.splits.values():
            yield from split.iter_items()
