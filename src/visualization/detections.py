import colorsys

import cv2
import numpy as np

from src.core.dto import Detection


class DetectionVisualizer:
    """
    Утилита визуализации детекций на кадре.
    """

    def __init__(
        self,
        classes: dict[int, str],
        box_thickness: int = 2,
        font_scale: float = 0.7,
        font_thickness: int = 2,
        text_padding: int = 4,
        text_color: tuple[int, int, int] = (255, 255, 255),
    ):
        """
        Инициализирует утилиту для отрисовки детекций.

        :param classes: Отображение индексов классов с их названиями.
        :type classes: dict[int, str]
        :param box_thickness: Толщина bbox'а.
        :type box_thickness: int, optional
        :param font_scale: Коэффициент масштабирования шрифта.
        :type font_scale: float, optional
        :param font_thickness: Тощина шрифта.
        :type font_thickness: int, optional
        :param text_padding: Паддинг между текстом и фоном под текстом.
        :type text_padding: int, optional
        :param text_color: Цвет текста.
        :type text_color: tuple[int, int, int], optional
        """
        self._classes = classes

        self._box_thickness = box_thickness
        self._font_scale = font_scale
        self._font_thickness = font_thickness
        self._text_padding = text_padding
        self._text_color = text_color

        self._class_colors = {
            class_id: self._get_color(class_id, len(self._classes))
            for class_id in classes
        }

    def plot_predictions(self, frame: np.ndarray, detections: list[Detection]) -> np.ndarray:
        """
        Отрисовывает детекции на кадре.

        :param frame: Исходный кадр.
        :type frame: np.ndarray
        :param detections: Список детекций на кадре.
        :type detections: list[Detection]
        :return: Кадр с отрисованными bbox'ами.
        :rtype: np.ndarray
        """
        img = frame.copy()

        for det in detections:
            x1, y1, x2, y2 = det.bbox

            label = self._classes.get(det.class_id, str(det.class_id))
            confidence = det.confidence
            color = self._class_colors.get(det.class_id, (255, 0, 0))

            text = f"{label} {confidence:.2f}"

            # Bounding box
            cv2.rectangle(
                img,
                (x1, y1),
                (x2, y2),
                color=color,
                thickness=self._box_thickness,
            )

            # Размер текста
            (text_w, text_h), baseline = cv2.getTextSize(
                text,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=self._font_scale,
                thickness=self._font_thickness,
            )

            # Фон под текстом
            cv2.rectangle(
                img,
                (x1, y1 - text_h - baseline - self._text_padding * 2),
                (x1 + text_w + self._text_padding * 2, y1),
                color=color,
                thickness=-1,
            )

            # Текст
            cv2.putText(
                img,
                text,
                (x1 + self._text_padding, y1 - baseline - self._text_padding),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=self._font_scale,
                color=self._text_color,
                thickness=self._font_thickness,
                lineType=cv2.LINE_AA,
            )

        return img

    @staticmethod
    def _get_color(class_id: int, total: int) -> tuple[int, int, int]:
        """
        Вычисляет HSV для индекса класса и преобразует его в RGB.

        Насыщенность (saturation) и значение (value) являются константными.
        Тон (hue) определяется отношением индекса класса к общему количеству классов.

        :param class_id: Индекс класса.
        :type class_id: int
        :param total: Общее количество классов
        :type total: int
        :return: Цвет для класса в формате RGB.
        :rtype: tuple[int, int, int]
        """
        hue = class_id / total
        saturation = 0.85
        value = 0.95

        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return int(r * 255), int(g * 255), int(b * 255)
