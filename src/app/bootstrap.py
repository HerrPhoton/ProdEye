from typing import Any
from pathlib import Path

import yaml

from src.utils import PathLike
from src.app.parsers import parse_camera, parse_detector, parse_checkout_input
from src.app.parsers import parse_checkout_output
from src.app.factories import build_camera, build_detector, build_checkout_input
from src.app.factories import build_checkout_output
from src.core.pipeline import VisualVerificationPipeline

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: PathLike) -> dict[str, Any]:
    """
    Считывает yaml-файл по указанному пути.

    :param path: Путь до .yaml.
    :type path: PathLike
    :return: Словарь, содержищий данные из yaml-файла.
    :rtype: dict[str, Any]
    """
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def bootstrap() -> VisualVerificationPipeline:

    CONFIGS_PATH = PROJECT_ROOT / "configs"

    camera_raw = load_yaml(CONFIGS_PATH / "camera.yaml")
    detector_raw = load_yaml(CONFIGS_PATH / "detector.yaml")
    checkout_input_raw = load_yaml(CONFIGS_PATH / "checkout_input.yaml")
    checkout_output_raw = load_yaml(CONFIGS_PATH / "checkout_output.yaml")

    camera_config = parse_camera(camera_raw)
    detector_config = parse_detector(detector_raw)
    checkout_input_config = parse_checkout_input(checkout_input_raw)
    checkout_output_config = parse_checkout_output(checkout_output_raw)

    camera = build_camera(camera_config)
    detector = build_detector(detector_config)
    checkout_input = build_checkout_input(checkout_input_config)
    checkout_output = build_checkout_output(checkout_output_config)

    return VisualVerificationPipeline(
        camera=camera,
        detector=detector,
        checkout_input=checkout_input,
        checkout_output=checkout_output,
    )
