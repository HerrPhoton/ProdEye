def normalize_class_mapping(class_names: list[str] | dict[int, str]) -> dict[int, str]:
    """
    Приводит список или словарь классов к формату ``dict[int, str]``, где
    ключ - это индекс класса, а значение - название класса.

    :param class_names: Список названий классов или словарь ``{id: name}``.
    :type class_names: list[str] | dict[int, str]
    :raises TypeError: Если ``class_names`` не является списком или словарем.
    :return: Нормализованный словарь классов.
    :rtype: dict[int, str]
    """
    if isinstance(class_names, dict):
        return {int(k): v for k, v in class_names.items()}

    if isinstance(class_names, list):
        return dict(enumerate(class_names))

    raise TypeError(
        "class_names must be list[str] or dict[int, str]"
    )
