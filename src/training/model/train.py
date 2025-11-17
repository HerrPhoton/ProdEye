from pathlib import Path

from ultralytics import YOLO

if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parent

    model = YOLO(ROOT / "../../models/yolo11n.pt")

    results = model.train(data=ROOT / "../../dataset/processed/v1/data.yaml",
                          epochs=200,
                          batch=16,
                          imgsz=640,
                          project=ROOT / "../runs")
