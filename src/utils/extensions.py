IMAGE_EXTENSIONS: tuple[str, ...] = (".png", ".jpg", ".jpeg")
LABEL_EXTENSIONS: tuple[str, ...] = (".txt",)


def normalize_extensions(extensions: set[str]) -> set[str]:
    """Нормализует расширения, добавляя точку перед расширением, если она не добавлена

    :param set[str] extensions: Расширения для нормализации
    :return set[str]: расширения
    """
    return {ext if ext.startswith('.') else f'.{ext}' for ext in extensions}
