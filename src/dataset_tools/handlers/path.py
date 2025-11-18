from pathlib import Path
from collections.abc import Iterable, Generator

from ...utils import PathLike, normalize_to_paths, validate_paths_exist


class PathHandler:

    def __init__(
        self,
        paths: PathLike | Iterable[PathLike],
        extensions: Iterable[str],
        recursive: bool = False,
    ):
        self.paths = normalize_to_paths(paths)
        self.extensions = {ext.lower() for ext in extensions}
        self.recursive = recursive

        validate_paths_exist(self.paths)

    def iter_files(self) -> Generator[Path, None, None]:
        """Итерируется по всем файлам в `self.paths` с указанным расширением.
        Если `recursive=True`, то обходит рекурсивно каждую директорию.

        :yield Generator[Path, None, None]: Путь до файла
        """
        for root in self.paths:
            iterator = root.rglob("*") if self.recursive else root.iterdir()
            for path in iterator:
                if path.is_file() and path.suffix.lower() in self.extensions:
                    yield path
