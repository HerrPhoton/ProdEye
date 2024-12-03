import os
import argparse
from dataclasses import dataclass

from tqdm import tqdm


@dataclass
class LabelCheckResult:
    has_class_error: bool
    has_bounds_error: bool
    fixed_lines: list[str]
    original_count: int
    final_count: int


class YOLOLabelsChecker:

    def __init__(self, labels_dir: str, fix_classes: bool = False, remove_invalid: bool = False, verbose: bool = None):
        self.labels_dir = labels_dir
        self.fix_classes = fix_classes
        self.remove_invalid = remove_invalid
        self.verbose = verbose if verbose is not None else (not (fix_classes or remove_invalid))

    def _check_line(self, values: tuple[float, float, float, float, float]) -> bool:
        """Проверяет, находятся ли значения в допустимом диапазоне [0, 1]"""
        n, x, y, w, h = values
        return all(0 <= value <= 1 for value in (x, y, w, h))

    def _process_label_file(self, label_path: str) -> LabelCheckResult:
        new_lines = []
        class_error = False
        bounds_error = False

        try:
            with open(label_path) as file:
                data = file.readlines()
                original_count = len(data)

                for line in data:
                    try:
                        values = tuple(map(float, line.strip().split()))
                        n, x, y, w, h = values

                        if n != 0 and not class_error and self.verbose:
                            tqdm.write(f'{os.path.basename(label_path)}: Номер класса не равен 0')
                            class_error = True

                        if not self._check_line(values) and not bounds_error and self.verbose:
                            tqdm.write(
                                f'{os.path.basename(label_path)}: Неверные значения в строке {x:.2f} {y:.2f} {w:.2f} {h:.2f}')
                            bounds_error = True

                        if (not self.remove_invalid or self._check_line(values)):
                            class_num = "0" if self.fix_classes else str(int(n))
                            new_lines.append(f"{class_num} {x} {y} {w} {h}\n")

                    except ValueError:
                        tqdm.write(f'{os.path.basename(label_path)}: Ошибка формата строки')
                        continue

        except Exception as e:
            tqdm.write(f'{os.path.basename(label_path)}: Ошибка чтения файла - {str(e)}')
            return LabelCheckResult(False, False, [], 0, 0)

        return LabelCheckResult(class_error, bounds_error, new_lines, original_count, len(new_lines))

    def process_labels(self):
        """Обрабатывает все файлы меток в указанной директории"""
        label_files = os.listdir(self.labels_dir)

        for label in tqdm(label_files, desc="Обработка меток"):
            label_path = os.path.join(self.labels_dir, label)
            result = self._process_label_file(label_path)

            if (self.fix_classes or self.remove_invalid) and result.fixed_lines:

                if result.final_count == 0 and self.verbose:
                    tqdm.write(f'{label}: Не осталось ни одной метки')

                elif result.final_count != result.original_count and self.verbose:
                    tqdm.write(f'{label}: Изменено меток: {result.original_count} -> {result.final_count}')

                with open(label_path, 'w') as file:
                    file.writelines(result.fixed_lines)


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--labels_dir", type=str, required=True, help="Директория с аннотациями")
    parser.add_argument("--fix_classes", action="store_true", help="Заменить все номера классов на 0")
    parser.add_argument("--remove_invalid", action="store_true", help="Удалить строки со значениями, не входящими в [0, 1]")
    parser.add_argument("-v",
                        "--verbose",
                        action="store_true",
                        help="Выводить информацию о поврежденных файлах. По умолчанию True, если не установлены флаги fix")

    args = parser.parse_args()

    checker = YOLOLabelsChecker(args.labels_dir,
                                fix_classes=args.fix_classes,
                                remove_invalid=args.remove_invalid,
                                verbose=args.verbose)
    checker.process_labels()


if __name__ == "__main__":
    main()
