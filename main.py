import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from controllers.search_controller import SearchController
from views.main_window import MainWindow


def load_stylesheet() -> str:
    style_path = Path(__file__).parent / "assets" / "styles" / "dark.qss"
    return style_path.read_text(encoding="utf-8")


app = QApplication(sys.argv)
app.setStyle("Fusion")
app.setStyleSheet(load_stylesheet())

window = MainWindow()
controller = SearchController(window)
window.search_controller = controller
window.show()

sys.exit(app.exec())
