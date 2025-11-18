import argparse

from ultralytics import YOLO


def test_images(input: str, model, conf: float, iou: float, save: bool):

    model.predict(source=input, conf=conf, iou=iou, save=save)
    return


def valid_images(model, conf: float, iou: float):

    model.val(data="data.yaml", imgsz=640, batch=16, conf=conf, iou=iou)
    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        "--function",
        type=str,
        default="valid",
        help="valid(metrics) or test(without metrics)",
    )
    parser.add_argument(
        '-i',
        "--input",
        type=str,
        default="../dataset/raw/Fruit Detection Dataset/test/images/",
        help="path to valid or test images",
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="../models/best.pt",
        help="model_path",
    )
    parser.add_argument(
        '--conf',
        type=float,
        default=0.5,
        help="confidence",
    )
    parser.add_argument(
        '--iou',
        type=float,
        default=0.5,
        help="iou",
    )
    parser.add_argument(
        '--save',
        action=argparse.BooleanOptionalAction,
        help="save images or --no-save",
    )
    args = parser.parse_args()

    model = YOLO('../models/best.pt')
    if args.function == 'test':
        test_images(args.input, model, args.conf, args.iou, args.save)
    if args.function == 'valid':
        valid_images(model, args.conf, args.iou)


if __name__ == "__main__":
    main()
