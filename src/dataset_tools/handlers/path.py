from pathlib import Path
from collections.abc import Iterable, Generator

from ...utils import PathLike, normalize_to_paths, normalize_extensions
from ...utils import validate_paths_exist


class PathHandler:

    def __init__(
        self,
        paths: PathLike | Iterable[PathLike],
        extensions: Iterable[str],
        recursive: bool = False,
    ):
        """
        Инициализирует менеджер для работы с путями до файлов.

        Преобразует указанные путь/пути ``paths`` к списку ``pathlib.Path``
        объектов. Для указанных расширений файлов формирует множество нормализованных
        (с ведущей точкой) расширений в нижнем регистре.

        :param paths: Путь/пути до директорий с файлами.
        :type paths: PathLike | Iterable[PathLike]
        :param extensions: Расширения обрабатываемых файлов.
        :type extensions: Iterable[str]
        :param recursive: Обходить ли указанные директории рекурсивно.
        :type recursive: bool, optional
        :raises ValueError: Если указанная директория/директории ``paths`` не найдены.
        """
        self.paths = normalize_to_paths(paths)
        self.extensions = normalize_extensions({ext.lower() for ext in extensions})
        self.recursive = recursive

        validate_paths_exist(self.paths)

    def iter_files(self) -> Generator[Path, None, None]:
        """
        Итерируется по всем файлам в :attr:`paths` с указанным расширением.
        Если :attr:`recursive` установлен в ``True``, обход выполняется рекурсивно.

        :return: Генератор путей к файлам.
        :rtype: Generator[pathlib.Path, None, None]
        """
        for root in self.paths:
            iterator = root.rglob("*") if self.recursive else root.iterdir()
            for path in iterator:
                if path.is_file() and path.suffix.lower() in self.extensions:
                    yield path
