class DatasetReducer:

    def __init__(self):
        pass

    def reduce_dataset(
        self,
        size: int | None = None,
        dir_sizes: dict[PathLike, int] | None = None,
        strategy: Literal["first", "last", "random"] = "random",
    ) -> dict[str, int]:
        """Уменьшает размер датасета путем удаления изображений и их меток
        с заданной стратегий отбора.

        :param int | None size: Целевой суммарный размер датасета для всех директорий`self.images_dir`.
                                Если указан, уменьшение происходит равномерно для всех директорий.
                                Взаимоисключающий с `dir_sizes`.
        :param dict[PathLike, int] | None dir_sizes: Целевые размеры отдельно для указанных директорий.
                                                     Ключи - пути к директориям, значения - целевые размеры.
                                                     Взаимоисключающий с `size`
        :param Literal["first", "last", "random"] strategy: Стратегия выбора удаляемых объектов.
                                                            - "first": удаляет первые объекты в списке
                                                            - "last": удаляет последние объекты в списке
                                                            - "random": удаляет случайные объекты в списке
        :raises ValueError: Если указаны одновременно `size` и `dir_sizes`, или если ни один из них не указан.
        :return dict[str, int]: Словарь с путями до директорий и их конечным размером
        """
        if size is not None and dir_sizes is not None:
            raise ValueError("Указаны одновременно `size` и `dir_sizes`")
        if size is None and dir_sizes is None:
            raise ValueError("Ни один из параметров `size` и `dir_sizes` не указан")
