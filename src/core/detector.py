import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from .config import settings
from .stream import VideoStream


class ProdDetector:

    def __init__(self, model_path: str):
        self.model = YOLO(model_path)
        self.classes = self.model.names

    def predict(self, image: np.ndarray) -> list[Results]:
        results = self.model.predict(source=image, conf=settings.MODEL_CONF, iou=settings.MODEL_IOU, verbose=False)
        return results

    def plot_predictions(self, results: list[Results]) -> np.ndarray:
        frame = results[0].plot()

        for result in results[1 :]:
            frame = result.plot(img=frame)

        return frame

    def stream_predict(self):

        def frame_handler(frame: np.ndarray) -> np.ndarray:
            results = self.predict(frame)
            if results:
                frame = self.plot_predictions(results)
            return frame

        stream = VideoStream()
        stream.show_stream(frame_handler=frame_handler)
