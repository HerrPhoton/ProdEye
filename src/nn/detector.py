import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from configs.yolo import YoloConfig
from src.core.stream import VideoStream


class ProdDetector:

    def __init__(self, model_path: str):
        self.model = YOLO(model_path)
        self.classes = self.model.names
        print("Available classes:", self.classes)

    def predict(self, image: np.ndarray) -> list[Results]:
        results = self.model.predict(
            source=image,
            conf=YoloConfig.CONF,
            iou=YoloConfig.IOU,
            verbose=False
        )
        return results

    def plot_predictions(self, results: list[Results]) -> np.ndarray:

        frame = results[0].plot()

        for result in results[1:]:
            frame = result.plot(img=frame)

        return frame

    def stream_predict(self):

        with VideoStream() as stream:

            for frame in stream:
                results = self.predict(frame)

                if results:
                    frame = self.plot_predictions(results)

                stream.visualize_frame(frame)
