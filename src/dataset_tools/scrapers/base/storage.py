from pathlib import Path

from icrawler.storage.filesystem import FileSystem


class PrefixFileSystemStorage(FileSystem):

    def __init__(self, root_dir: str, filename_prefix: str):
        self.root_dir = root_dir
        self.prefix = filename_prefix

    def max_file_idx(self) -> int:
        max_idx = 0

        for p in Path(self.root_dir).iterdir():
            if not p.is_file():
                continue

            stem = p.stem
            if not stem.startswith(self.prefix):
                continue

            try:
                idx = int(stem[len(self.prefix):])
            except ValueError:
                continue

            if idx > max_idx:
                max_idx = idx

        return max_idx
