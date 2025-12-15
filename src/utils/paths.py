from pathlib import Path
from collections.abc import Iterable

from .types import PathLike


def normalize_to_paths(paths: PathLike | Iterable[PathLike]) -> list[Path]:
    """
    Преобразует путь/пути к списку ``pathlib.Path`` объектов.

    :param paths: Путь/пути до файлов/директорий.
    :type paths: PathLike | Iterable[PathLike]
    :return: Список путей в виде ``pathlib.Path`` объектов.
    :rtype: list[pathlib.Path]
    """
    if isinstance(paths, (str, Path)):
        return [Path(paths)]
    return [Path(p) for p in paths]


def validate_paths_exist(paths: PathLike | Iterable[PathLike]) -> None:
    """
    Проверяет существование указанных директорий.

    :param paths: Путь/пути до директорий.
    :type paths: PathLike | Iterable[PathLike]
    :raises ValueError: Если указанные директории не существуют.
    """
    if not isinstance(paths, Iterable):
        paths = [paths]

    path_objects = [Path(p) for p in paths]
    missing_dirs = [d for d in path_objects if not d.exists()]

    if missing_dirs:
        raise ValueError(f"The directories do not exist: {', '.join(map(str, missing_dirs))}")
