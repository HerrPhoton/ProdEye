IMAGE_EXTENSIONS: tuple[str, ...] = (".png", ".jpg", ".jpeg")
LABEL_EXTENSIONS: tuple[str, ...] = (".txt",)


def normalize_extensions(extensions: set[str]) -> set[str]:
    """
    Нормализует расширения, добавляя точку перед расширением, если она не добавлена.

    :param extensions: Расширения для нормализации.
    :type extensions: set[str]
    :return: Нормализованные расширения.
    :rtype: set[str]
    """
    return {ext if ext.startswith('.') else f'.{ext}' for ext in extensions}
