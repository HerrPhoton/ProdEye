import sys

from PyQt6.QtWidgets import QApplication

from .ui.main import ProdDetectionApp
from .core.config import settings


def main():
    app = QApplication(sys.argv)
    window = ProdDetectionApp(detector_model_path=str(settings.MODEL_PATH))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
