from datetime import datetime

import cv2
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel, QWidget, QComboBox
from PyQt6.QtWidgets import QHBoxLayout, QHeaderView
from PyQt6.QtWidgets import QMainWindow, QPushButton
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtWidgets import QAbstractItemView

from ..core.basket import Basket, ProductStatus
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

        self.basket = Basket()
        self.verification_timeout = 10  # секунд на проверку товара
        self.last_verification_time = None

        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def init_ui(self):
        """Инициализация элементов интерфейса."""
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Левая панель с видео
        video_panel = QVBoxLayout()
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)  # Минимальный размер видео
        video_panel.addWidget(self.video_label)

        # Правая панель с корзиной
        basket_panel = QVBoxLayout()

        # Выбор продукта (имитация сканера)
        scanner_group = QWidget()
        scanner_layout = QVBoxLayout()
        scanner_layout.setSpacing(5)  # Уменьшаем расстояние между элементами

        self.fruit_selector = QComboBox()
        self.fruit_selector.addItems(self.detector.classes.values())
        scanner_layout.addWidget(QLabel("Сканер товаров:"))
        scanner_layout.addWidget(self.fruit_selector)

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
        self.basket_table.horizontalHeader().setStretchLastSection(True)  # Растягиваем последнюю колонку
        self.basket_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)  # Автоматическая ширина колонок
        self.basket_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)  # Автоматическая высота строк
        self.basket_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)  # Плавная прокрутка

        # Устанавливаем политику размера для таблицы
        self.basket_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        basket_panel.addWidget(self.basket_table)

        # Добавляем панели в главный layout с указанием пропорций
        main_layout.addLayout(video_panel, stretch=2)
        main_layout.addLayout(basket_panel, stretch=1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Устанавливаем минимальный размер окна
        self.setMinimumSize(1024, 768)

    def scan_product(self):
        product = self.fruit_selector.currentText()
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

            # Проверяем таймаут
            if (current_time - self.last_verification_time).seconds > self.verification_timeout:
                self.basket.current_item.status = ProductStatus.EXPIRED
                self.basket.current_item = None
            else:
                # Получаем количество уже проверенных товаров этого типа
                verified_counts = self.basket.get_verified_counts()
                verified_count = verified_counts[self.basket.current_item.product_name]

                # Проверяем, есть ли новый объект в кадре
                match_found = self.matcher.is_match(self.basket.current_item.product_name, frame, verified_count)

                if match_found:
                    self.basket.verify_current_item()

            self.update_basket_table()

        # Отображение кадра
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.stream.close_stream()
        event.accept()
