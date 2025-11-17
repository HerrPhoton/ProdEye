import argparse
from pathlib import Path


class ImagesRenamer:

    def __init__(self, images_dir: str, labels_dir: str | None = None, new_name: str | None = None, recursive: bool = False):
        self.images_dir = Path(images_dir)
        self.labels_dir = Path(labels_dir) if labels_dir else None
        self.new_name = new_name
        self.recursive = recursive
        self.valid_extensions = {'.jpg', '.png', '.jpeg'}
        self.index = 0

    def _get_new_name(self, name: str, prefix: str = '') -> str:
        if self.new_name:
            new_name = f'{self.new_name}_{self.index}{Path(name).suffix}'
            self.index += 1
        else:
            new_name = f'{prefix}_{name}' if prefix else name
        return new_name

    def _rename_files(self, image_path: Path, name: str, new_name: str) -> None:
        # Переименование изображения
        image_path.rename(image_path.parent / new_name)

        # Переименование метки, если указана директория с метками
        if self.labels_dir:
            label_path = self.labels_dir / image_path.relative_to(self.images_dir).parent / Path(name).with_suffix('.txt')
            if label_path.exists():
                label_path.rename(label_path.parent / Path(new_name).with_suffix('.txt'))

    def rename_images(self) -> None:
        if self.recursive:
            for image_path in self.images_dir.rglob('*'):
                if not image_path.is_file() or image_path.suffix.lower() not in self.valid_extensions:
                    continue

                rel_path = image_path.parent.relative_to(self.images_dir)
                prefix = '_'.join(rel_path.parts) if str(rel_path) != '.' else self.images_dir.name
                new_name = self._get_new_name(image_path.name, prefix)
                self._rename_files(image_path, image_path.name, new_name)
        else:
            for image_path in self.images_dir.iterdir():
                if not image_path.is_file() or image_path.suffix.lower() not in self.valid_extensions:
                    continue

                new_name = self._get_new_name(image_path.name, self.images_dir.name)
                self._rename_files(image_path, image_path.name, new_name)


def main():
    parser = argparse.ArgumentParser(description="Переименование изображений и их меток")
    parser.add_argument("--images_dir", type=str, required=True, help="Путь до директории с изображениями/поддиректориями")
    parser.add_argument("--labels_dir", type=str, default=None, help="Путь до директории с аннотациями")
    parser.add_argument("-r", "--recursive", action="store_true", help="Переименовать изображения во всех поддиректориях")
    parser.add_argument("-n", "--new_name", type=str, default=None, help="Новое имя для изображений (с индексом)")

    args = parser.parse_args()

    renamer = ImagesRenamer(images_dir=args.images_dir,
                            labels_dir=args.labels_dir,
                            new_name=args.new_name,
                            recursive=args.recursive)
    renamer.rename_images()


if __name__ == "__main__":
    main()
