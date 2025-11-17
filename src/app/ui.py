from datetime import datetime

import cv2
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QLabel, QWidget, QComboBox, QHBoxLayout, QHeaderView
from PyQt6.QtWidgets import QMainWindow, QPushButton, QSizePolicy, QVBoxLayout
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView

from app.src.core.basket import Basket, ProductStatus
from app.src.core.stream import VideoStream
from app.src.core.matcher import ProdMatcher
from app.src.core.detector import ProdDetector


class ProdDetectionApp(QMainWindow):

    def __init__(self, detector_model_path: str):
        super().__init__()

        self.setWindowTitle("ProdEye")
        self.showMaximized()
        self.setFixedSize(self.size())
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FCFDFE,
                    stop:1 #739F3d
                );
            }

            QLabel {
                color: #2C3E50;
                font-size: 14px;
            }

            QPushButton {
                background-color: #739F3d;
                color: white;
                border: none;
                padding: 5px;
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

            QTableWidget {
                background-color: #fcfdfe;
                border: 1px solid #ee693f;
                border-radius: 5px;
                alternate-background-color: #F0F0F0;
                gridline-color: #E0E0E0;
            }

            QHeaderView::section {
                background-color: #ee693f;
                color: white;
                padding: 20px;
            }
        """)
        self.stream = VideoStream()
        self.detector = ProdDetector(detector_model_path)
        self.matcher = ProdMatcher(self.detector)

        self.basket = Basket()
        self.verification_timeout = 10
        self.last_verification_time = None

        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def init_ui(self):
        """Инициализация элементов интерфейса."""
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Левая панель
        video_container = QWidget()
        video_container.setStyleSheet("""
            border: 3px solid #ee693f;
            border-radius: 5px;
            padding: 10px;
        """)
        video_panel = QVBoxLayout(video_container)

        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        video_panel.addStretch(1)
        video_panel.addWidget(self.video_label, alignment=Qt.AlignmentFlag.AlignCenter)
        video_panel.addStretch(1)

        video_panel.setContentsMargins(10, 10, 10, 10)

        basket_container = QWidget()

        basket_panel = QVBoxLayout(basket_container)

        # Выбор продукта (имитация сканера)
        scanner_group = QWidget()
        scanner_layout = QVBoxLayout()
        scanner_layout.setSpacing(5)

        self.prod_selector = QComboBox()
        self.prod_selector.addItems(self.detector.classes.values())
        scanner_layout.addWidget(QLabel("Сканер товаров:"))
        scanner_layout.addWidget(self.prod_selector)

        self.scan_button = QPushButton("Отсканировать")
        self.scan_button.clicked.connect(self.scan_product)
        scanner_layout.addWidget(self.scan_button)

        scanner_group.setLayout(scanner_layout)
        basket_panel.addWidget(scanner_group)

        # Таблица корзины
        basket_panel.addWidget(QLabel("Корзина:"))

        self.basket_table = QTableWidget()
        self.basket_table.setColumnCount(3)
        self.basket_table.setHorizontalHeaderLabels(["Товар", "Статус", "Время"])

        # Настройка таблицы
        self.basket_table.horizontalHeader().setStretchLastSection(True)
        self.basket_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.basket_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.basket_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.basket_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        basket_panel.addWidget(self.basket_table)

        main_layout.addWidget(video_container, stretch=2)
        main_layout.addWidget(basket_container, stretch=1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setMinimumSize(1024, 768)

    def scan_product(self):
        product = self.prod_selector.currentText()
        self.basket.add_item(product)
        self.update_basket_table()
        self.last_verification_time = datetime.now()

    def update_basket_table(self):
        self.basket_table.setRowCount(len(self.basket.items))
        for i, item in enumerate(self.basket.items):
            self.basket_table.setItem(i, 0, QTableWidgetItem(item.product_name))
            self.basket_table.setItem(i, 1, QTableWidgetItem(item.status.value))
            time_str = item.verified_at.strftime("%H:%M:%S") if item.verified_at else "-"
            self.basket_table.setItem(i, 2, QTableWidgetItem(time_str))

    def update_frame(self):
        frame = self.stream.read_frame()
        if frame is None:
            return

        results = self.detector.predict(frame)
        if results:
            frame = self.detector.plot_predictions(results)

        # Проверка текущего товара
        if self.basket.current_item:
            current_time = datetime.now()

            if (current_time - self.last_verification_time).seconds > self.verification_timeout:
                self.basket.current_item.status = ProductStatus.EXPIRED
                self.basket.current_item = None

            else:
                verified_counts = self.basket.get_verified_counts()
                verified_count = verified_counts[self.basket.current_item.product_name]

                # Проверяем, есть ли новый объект в кадре
                match_found = self.matcher.is_match(self.basket.current_item.product_name, frame, verified_count)

                if match_found:
                    self.basket.verify_current_item()

            self.update_basket_table()

        scaled_frame = cv2.resize(frame, (1280, 960), interpolation=cv2.INTER_AREA)

        rgb_frame = cv2.cvtColor(scaled_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.stream.close_stream()
        event.accept()
