from collections.abc import Callable

import cv2


class VideoStream:

    def __init__(self, source: int = 0):
        self.source = source
        self.cap = cv2.VideoCapture(self.source)

        if not self.cap.isOpened():
            raise ValueError(f"Не удалось открыть видеопоток из источника {source}.")

    def read_frame(self):

        ret, frame = self.cap.read()

        if not ret:
            return None

        return frame

    def show_stream(self, frame_handler: Callable | None = None, window_name: str = "Video Stream"):

        print("Нажмите 'q', чтобы выйти из режима просмотра видеопотока.")

        while True:
            frame = self.read_frame()
            if frame is None:
                print("Ошибка чтения кадра. Завершение.")
                break

            if frame_handler:
                frame = frame_handler(frame)

            cv2.imshow(window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Выход из режима просмотра видеопотока.")
                break

        self.close_stream()

    def close_stream(self):
        self.cap.release()
        cv2.destroyAllWindows()
