import cv2
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel, QWidget, QComboBox
from PyQt6.QtWidgets import QMainWindow, QPushButton
from PyQt6.QtWidgets import QVBoxLayout

from ..core.stream import VideoStream
from ..core.matcher import ProdMatcher
from ..core.detector import ProdDetector


class ProdDetectionApp(QMainWindow):

    def __init__(self, detector_model_path: str):
        super().__init__()

        self.setWindowTitle("Детекция продуктов")
        self.setGeometry(100, 100, 800, 600)

        self.stream = VideoStream()
        self.detector = ProdDetector(detector_model_path)
        self.matcher = ProdMatcher(self.detector)

        self.selected_prod = None

        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def init_ui(self):
        """Инициализация элементов интерфейса."""
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.info_label = QLabel("Выберите продукт:")
        layout.addWidget(self.info_label)

        self.fruit_selector = QComboBox()
        self.fruit_selector.addItems(self.detector.classes.values())
        self.fruit_selector.currentTextChanged.connect(self.on_fruit_selected)
        layout.addWidget(self.fruit_selector)

        self.start_button = QPushButton("Начать обработку")
        self.start_button.clicked.connect(self.start_processing)
        layout.addWidget(self.start_button)

        self.video_label = QLabel()
        layout.addWidget(self.video_label)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_fruit_selected(self, fruit_name: str):
        self.selected_prod = fruit_name
        self.info_label.setText(f"Выбран продукт: {fruit_name}")

    def start_processing(self):

        if not self.selected_prod:
            self.info_label.setText("Пожалуйста, выберите продукт.")
            return

        self.info_label.setText(f"Идёт обработка для: {self.selected_prod}")

    def update_frame(self):
        frame = self.stream.read_frame()
        if frame is None:
            return

        results = self.detector.predict(frame)

        if results:
            frame = self.detector.plot_predictions(results)

        if self.selected_prod:
            match_found = self.matcher.is_match(self.selected_prod, frame)
            status = "НАЙДЕН ✅" if match_found else "НЕ НАЙДЕН ❌"
            self.info_label.setText(f"Продукт '{self.selected_prod}': {status}")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.stream.close_stream()
        event.accept()
