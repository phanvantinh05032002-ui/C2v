from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from views.log_panel import LogPanel
from views.search_panel import SearchPanel
from views.table_view import ChannelTable


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("C2V KEY")
        self.resize(1280, 820)
        self.setMinimumSize(1180, 760)

        central = QWidget()
        central.setObjectName("mainWindow")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(10, 10, 10, 10)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.search_tab = QWidget()
        self.analysis_tab = QWidget()

        self.tabs.addTab(self.search_tab, "Tìm kênh")
        self.tabs.addTab(self.analysis_tab, "Phân tích kênh")

        self._build_search_tab()
        self._build_analysis_tab()

        root_layout.addWidget(self.tabs)

    def _build_search_tab(self):
        layout = QVBoxLayout(self.search_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.search_panel = SearchPanel()
        self.table_filter_input = QLineEdit()
        self.table_filter_input.setPlaceholderText(
            "Lọc nhanh (theo bất kỳ cột nào)..."
        )
        self.table = ChannelTable()
        self.import_btn = QPushButton("Import CSV")
        self.import_btn.setObjectName("secondaryButton")
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.setObjectName("secondaryButton")
        self.log_panel = LogPanel()

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Lọc:"))
        filter_row.addWidget(self.table_filter_input)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        action_row.addWidget(self.import_btn)
        action_row.addWidget(self.export_btn)

        layout.addWidget(self.search_panel)
        layout.addLayout(filter_row)
        layout.addWidget(self.table, 1)
        layout.addLayout(action_row)
        layout.addWidget(self.log_panel)

    def _build_analysis_tab(self):
        layout = QVBoxLayout(self.analysis_tab)
        placeholder = QLabel("Màn hình phân tích kênh sẽ được bổ sung tại đây.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setObjectName("placeholderLabel")
        layout.addWidget(placeholder)
