from pathlib import Path
from collections.abc import Iterable

from .types import PathLike


def normalize_to_paths(paths: PathLike | Iterable[PathLike]) -> list[Path]:
    """Преобразует путь/пути к списку Path объектов.

    :param PathLike | Iterable[PathLike] paths: Путь/пути
    :return list[Path]: Список путей
    """
    if isinstance(paths, (str, Path)):
        return [Path(paths)]
    return [Path(p) for p in paths]


def validate_paths_exist(paths: PathLike | Iterable[PathLike]) -> None:
    """Проверяет существование указанных директорий.

    :param PathLike | Iterable[PathLike] paths: Путь/пути до директорий
    :raises ValueError: Если указанные директории не существуют
    """
    if not isinstance(paths, Iterable):
        paths = [paths]

    path_objects = [Path(p) for p in paths]
    missing_dirs = [d for d in path_objects if not d.exists()]

    if missing_dirs:
        raise ValueError(f"Директории не существуют: {', '.join(map(str, missing_dirs))}")
