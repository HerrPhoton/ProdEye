import os
import argparse

from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=True)

    parser.add_argument(
        "--labels_dir",
        type=str,
        help="Директория с аннотациями.",
    )

    parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        help="Нужно ли удалить строки cо значениями, не входящими в [0, 1], и/или заменить номера классов на 0.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Нужно ли выводить информацию о поврежденных файлах. По умолчанию True, если не установлен фалг fix",
    )

    args = parser.parse_args()
    verbose = True if not args.fix else args.verbose

    for label in tqdm(os.listdir(args.labels_dir), leave=False):

        new_lines = []
        bounds_error = False
        class_error = False

        with open(os.path.join(args.labels_dir, label)) as file:
            data = file.readlines()

            for line in data:

                n, x, y, w, h = map(float, line.strip().split())

                if n != 0 and not class_error and verbose:
                    tqdm.write(f'{label}: Номер класса не равен 0')
                    class_error = True

                if any([value > 1 or value < 0 for value in [x, y, w, h]]) and not bounds_error and verbose:
                    tqdm.write(f'{label}: Неверные значения в строке {x:.2f} {y:.2f} {w:.2f} {h:.2f}')
                    bounds_error = True
                    break

                if args.fix:
                    new_lines.append(f"0 {x} {y} {w} {h}\n")

            if len(data) != 0 and len(new_lines) == 0 and args.fix and verbose:
                tqdm.write(f'{label}: Не осталось ни одной метки')

        if args.fix:
            with open(os.path.join(args.labels_dir, label), 'w') as file:
                file.writelines(new_lines)
