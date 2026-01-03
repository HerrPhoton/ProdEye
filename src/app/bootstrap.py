from typing import Any
from pathlib import Path

import yaml

from src.utils import PathLike
from src.app.parsers import parse_camera, parse_detector, parse_verifier
from src.app.parsers import parse_checkout_input, parse_checkout_output
from src.app.factories import build_camera, build_detector, build_verifier
from src.app.factories import build_checkout_input, build_checkout_output
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
    verifier_raw = load_yaml(CONFIGS_PATH / "verifier.yaml")
    checkout_input_raw = load_yaml(CONFIGS_PATH / "checkout_input.yaml")
    checkout_output_raw = load_yaml(CONFIGS_PATH / "checkout_output.yaml")

    camera_config = parse_camera(camera_raw)
    detector_config = parse_detector(detector_raw)
    verifier_config = parse_verifier(verifier_raw)
    checkout_input_config = parse_checkout_input(checkout_input_raw)
    checkout_output_config = parse_checkout_output(checkout_output_raw)

    camera = build_camera(camera_config)
    detector = build_detector(detector_config)
    verifier = build_verifier(verifier_config, classes=detector.get_classes())
    checkout_input = build_checkout_input(checkout_input_config)
    checkout_output = build_checkout_output(checkout_output_config)

    return VisualVerificationPipeline(
        camera=camera,
        detector=detector,
        verifier=verifier,
        checkout_input=checkout_input,
        checkout_output=checkout_output,
    )
