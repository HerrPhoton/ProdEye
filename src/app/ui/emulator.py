import time
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from src.core.dto import CheckoutRequest, VisualCheckStatus
from src.core.pipeline import VisualVerificationPipeline
from src.visualization import DetectionVisualizer
from src.adapters.checkout.inputs.ui import UICheckoutInput
from src.adapters.checkout.outputs.ui import UICheckoutOutput

from .widgets import CameraWidget, ResultWidget, CheckoutControlWidget

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ICON_PATH = str(PROJECT_ROOT / "assets" / "icons" / "ProdEye.ico")


class CheckoutEmulator(QWidget):
    """
    PyQt-эмулятор кассы самообслуживания.
    """

    def __init__(self, pipeline: VisualVerificationPipeline):
        """
        Инициализация эмулятора кассы самообслуживания с
        системой визуальной проверки товаров.

        :param pipeline: Экземпляр пайплайна визуальной проверки.
        :type pipeline: VisualVerificationPipeline
        """
        super().__init__()

        self.pipeline = pipeline

        # Проверка конфигурации запросов и ответов кассы
        self._checkout_input = self._require_ui_input()
        self._checkout_output = self._require_ui_output()

        # Подготовка окна UI
        self._setup_window()
        self._setup_ui()

        self._overlay = DetectionVisualizer(
            classes=self.pipeline.detector.get_classes()
        )

        # Настройка таймера для вызова шага пайплайна
        fps = self.pipeline.camera.get_actual_properties().fps
        self._pipeline_interval_ms = int(1000 / fps)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def _setup_window(self) -> None:
        """Настройка параметров окна UI."""

        # Настройка информации окна
        self.setWindowTitle("ProdEye")
        self.setWindowIcon(QIcon(ICON_PATH))

        # Настройка размеров окна
        self.resize(1280, 800)
        self.setFixedSize(self.size())

        # Настройка стилей виджетов
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FCFDFE,
                    stop:1 #739F3d
                );
            }
            QLabel {
                color: #2C3E50;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #739F3d;
                font-size: 12pt;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #7aa802;
            }
            QComboBox {
                background-color: #fcfdfe;
                border: 1px solid #ee693f;
                border-radius: 3px;
                padding: 5px;
            }
            QGroupBox {
                border: 1px solid #ee693f;
                border-radius: 5px;
                margin-top: 10px;
                font-size: 16pt;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                top: -8px;
            }
        """)

    def _setup_ui(self) -> None:
        """Размещение виджетов в окне UI."""

        main_layout = QHBoxLayout(self)
        side_panel = QVBoxLayout()

        self.camera_widget = CameraWidget(self.pipeline.camera)
        self.control_widget = CheckoutControlWidget(
            products=list(self.pipeline.detector.get_classes().values()),
            on_scan=self._on_scan,
        )
        self.result_widget = ResultWidget()

        # Правая панель со сканером и результатом
        side_panel.addWidget(self.control_widget)
        side_panel.addWidget(self.result_widget)
        side_panel.addStretch()

        # Левая панель с видео
        main_layout.addWidget(self.camera_widget, stretch=2)
        main_layout.addLayout(side_panel, stretch=1)

        self.setLayout(main_layout)

    def _require_ui_input(self) -> UICheckoutInput:
        """
        Проверка типа модели запросов от кассы.
        Для эмулятора кассы требуется указание типа ``type=ui``
        в конфигурации ``configs/checkout_input.yaml``.

        :raises RuntimeError: Если тип модели запросов от кассы не соответствует UI.
        :return: Экземпляр модель запросов от кассы из пайплайна.
        :rtype: UICheckoutInput
        """
        if not isinstance(self.pipeline.checkout_input, UICheckoutInput):
            raise RuntimeError(
                "CheckoutEmulator requires checkout_input type=ui "
                "(see configs/checkout_input.yaml)"
            )
        return self.pipeline.checkout_input

    def _require_ui_output(self) -> UICheckoutOutput:
        """
        Проверка типа модели результатов для кассы.
        Для эмулятора кассы требуется указание типа ``type=ui``
        в конфигурации ``configs/checkout_output.yaml``.

        :raises RuntimeError: Если тип модели результатов для кассы не соответствует UI.
        :return: Экземпляр модель результатов для кассы из пайплайна.
        :rtype: UICheckoutOutput
        """
        if not isinstance(self.pipeline.checkout_output, UICheckoutOutput):
            raise RuntimeError(
                "CheckoutEmulator requires checkout_output type=ui "
                "(see configs/checkout_output.yaml)"
            )
        return self.pipeline.checkout_output

    def _on_scan(self, product_label: str) -> None:
        """
        Колбэк, вызываемый после сканирования товара.

        :param product_label: Название отсканированного товара.
        :type product_label: str
        """
        # Формирование запроса от кассы
        request = CheckoutRequest(label=product_label, timestamp=time.time())
        self._checkout_input.put(request)

        # Переход системы в активное состояние
        self.result_widget.reset()
        self._timer.start(self._pipeline_interval_ms)
        self.camera_widget.stop_stream()

    def _tick(self) -> None:
        """Шаг работы пайплайна, вызываемый по таймеру."""
        step = self.pipeline.run_once()

        # Отрисовка детекций на кадре
        frame = step.frame
        if step.detections:
            frame = self._overlay.plot_predictions(frame, step.detections)

        # Визуализация кадра в виджете,
        # обновление виджета с результатами работы
        self.camera_widget.show_frame(frame)
        self.result_widget.update(step.result)

        # Переход в idle состояние при получении финального ответа
        if step.result.status != VisualCheckStatus.PENDING:
            self._timer.stop()
            self.camera_widget.start_stream()
