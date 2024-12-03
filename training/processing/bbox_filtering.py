import os
import argparse

from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=True)

    parser.add_argument(
        "--labels_dir",
        type=str,
        dest='labels_dir',
        help="Путь до директории с аннотациями.",
    )

    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        dest='threshold',
        default=0.07,
        help="Порог для отсеивания bbox.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Нужно ли выводить информацию об измененных файлах.",
    )

    args = parser.parse_args()

    for label in tqdm(os.listdir(args.labels_dir)):
        with open(os.path.join(args.labels_dir, label)) as file:
            lines = file.readlines()
            new_lines = []

            for line in lines:
                n, x, y, w, h = map(float, line.strip().split())

                if h >= args.threshold and w >= args.threshold:
                    new_lines.append(line)

            if args.verbose and len(lines) != len(new_lines):
                tqdm.write(f'{label}: Удалено {len(lines) - len(new_lines)} меток')

        with open(os.path.join(args.labels_dir, label), 'w') as file:
            file.writelines(new_lines)
