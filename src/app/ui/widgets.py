from collections.abc import Callable

import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QLabel, QWidget, QComboBox, QGroupBox, QPushButton
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout

from src.core.dto import VisualCheckResult, VisualCheckStatus
from src.core.ports import Camera


class CameraWidget(QWidget):
    """
    Виджет отображения видеопотока.
    """

    def __init__(self, camera: Camera):
        """
        Инициализация виджета для отображения видеопотока.

        :param camera: Экземпляр камеры с видеопотоком.
        :type camera: Camera
        """
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                border: 3px solid #ee693f;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        self._camera = camera

        # Настройка подложки для отображения видеопотока
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumSize(640, 480)
        self.label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(10, 10, 10, 10)

        # Настройка таймера для отоборажения видепотока
        fps = camera.get_actual_properties().fps
        self._interval_ms = int(1000 / fps)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_frame)
        self.start_stream()

    def show_frame(self, frame: np.ndarray) -> None:
        """
        Отображает кадр в UI.

        :param frame: Кадр для отображения.
        :type frame: numpy.ndarray
        """
        height, width, channels = frame.shape
        bytes_per_line = channels * width

        qt_image = QImage(
            frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        )

        pixmap = QPixmap.fromImage(qt_image)
        pixmap = pixmap.scaled(
            self.label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.label.setPixmap(pixmap)

    def start_stream(self) -> None:
        """Запускает таймер для отображения видеопотока."""
        self._timer.start(self._interval_ms)

    def stop_stream(self) -> None:
        """Останавливает таймер для отображения видеопотока."""
        self._timer.stop()

    def _update_frame(self) -> None:
        """Считывает кадр из видеопотока и отображает в UI."""
        frame = self._camera.read()
        self.show_frame(frame)


class CheckoutControlWidget(QGroupBox):
    """
    Виджет имитации сканера товаров.
    """

    def __init__(self, products: list[str], on_scan: Callable[[str], None]):
        """
        Инициализация виджета для имитации сканера товаров.

        :param products: Список доступных для сканирования продуктов.
        :type products: list[str]
        :param on_scan: Колбэк, вызываемый после сканирования товара.
        :type on_scan: Callable[[str], None]
        """
        super().__init__("Сканер товаров")

        self.setStyleSheet("""
            QWidget {
                padding: 10px;
            }
        """)

        self._on_scan = on_scan

        layout = QVBoxLayout()

        # Выпадающий список с продуктами
        self.product_box = QComboBox()
        self.product_box.addItems(products)

        # Кнопка для начала сканирования
        self.scan_button = QPushButton("Отсканировать")
        self.scan_button.clicked.connect(self._handle_scan)

        layout.addWidget(QLabel("Товар:"))
        layout.addWidget(self.product_box)
        layout.addWidget(self.scan_button)

        self.setLayout(layout)

    def _handle_scan(self) -> None:
        """Колбэк, вызываемый после нажатия на кнопку сканирования."""
        product = self.product_box.currentText()
        self._on_scan(product)


class ResultWidget(QGroupBox):
    """
    Виджет отображения результата визуальной проверки.
    """

    def __init__(self):
        """Инициализация виджета для отображения результата визуальной проверки."""
        super().__init__("Результат проверки")

        self.setStyleSheet("""
            QWidget {
                padding: 10px;
            }
        """)

        self._last_status: VisualCheckStatus | None = None

        layout = QVBoxLayout()

        # Поле со статусом проверки
        self.status_label = QLabel("Ожидание проверки")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px;")

        # Поле с полученной уверенностью детекции
        self.confidence_label = QLabel("")
        self.confidence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Поле с названием распознанного товара
        self.detected_label = QLabel("")
        self.detected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.status_label)
        layout.addWidget(self.confidence_label)
        layout.addWidget(self.detected_label)

        self.setLayout(layout)

    def reset(self) -> None:
        """Переводит систему в режим ожидания окончания проверки."""
        self._last_status = VisualCheckStatus.PENDING
        self.status_label.setText("Ожидание проверки")
        self.status_label.setStyleSheet("color: orange; font-size: 16px;")
        self.confidence_label.setText("")
        self.detected_label.setText("")

    def update(self, result: VisualCheckResult) -> None:
        """
        Обновляет информацию на виджете текущим результатом проверки.

        :param result: Результат визуальной проверки.
        :type result: VisualCheckResult
        """
        if result.status == self._last_status:
            return

        self._last_status = result.status

        match result.status:
            case VisualCheckStatus.PENDING:
                self.reset()
                return

            case VisualCheckStatus.MATCH:
                self.status_label.setText("Товар подтверждён")
                self.status_label.setStyleSheet("color: green; font-size: 16px;")

            case VisualCheckStatus.MISMATCH:
                self.status_label.setText("Несоответствие товара")
                self.status_label.setStyleSheet("color: red; font-size: 16px;")

        if result.confidence is not None:
            self.confidence_label.setText(
                f"Confidence: {result.confidence:.2f}"
            )

        if result.detected_label is not None:
            self.detected_label.setText(
                f"Распознанный товар: {result.detected_label}"
            )
