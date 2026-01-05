import sys

from PyQt6.QtWidgets import QApplication

from src.app.ui import CheckoutEmulator
from src.app.bootstrap import bootstrap


def main():
    pipeline = bootstrap()

    app = QApplication(sys.argv)
    window = CheckoutEmulator(pipeline)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
