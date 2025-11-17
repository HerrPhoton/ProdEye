from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[2]

WEIGHTS_PATH = ROOT_PATH / "weights"
YOLO_PATH = WEIGHTS_PATH / "best.pt"
