import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from PyQt6.QtWidgets import QApplication

from app.src.ui.main import ProdDetectionApp
from app.configs.config import settings


def main():
    app = QApplication(sys.argv)
    window = ProdDetectionApp(detector_model_path=str(settings.MODEL_PATH))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
