from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)


class AnalysisPanel(QWidget):

    def __init__(self):
        super().__init__()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Kênh:"))

        self.channel_id_input = QLineEdit()
        self.channel_id_input.setPlaceholderText("Nhập channel ID...")
        top_row.addWidget(self.channel_id_input, 1)

        self.filter_frame = self._build_filter_frame()
        top_row.addWidget(self.filter_frame)

        self.analyze_btn = QPushButton("Phân tích")
        self.analyze_btn.setObjectName("primaryButton")
        top_row.addWidget(self.analyze_btn)

        self.status_label = QLabel("Sẵn sàng phân tích.")
        self.status_label.setObjectName("fieldLabel")

        summary_frame = QFrame()
        summary_frame.setObjectName("panelCard")
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(8, 8, 8, 8)
        summary_layout.setSpacing(6)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(150)
        summary_layout.addWidget(self.summary_text)

        self.video_table = QTableWidget()
        self.video_table.setColumnCount(9)
        self.video_table.setHorizontalHeaderLabels(
            [
                "STT",
                "Tiêu đề",
                "Video ID",
                "Ngày đăng",
                "Thời lượng",
                "Loại video",
                "Lượt xem",
                "Bình luận",
                "URL",
            ]
        )
        self.video_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.video_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.video_table.setAlternatingRowColors(True)
        self.video_table.setShowGrid(False)
        self.video_table.verticalHeader().setVisible(False)
        self.video_table.verticalHeader().setDefaultSectionSize(30)

        header = self.video_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)

        root_layout.addLayout(top_row)
        root_layout.addWidget(self.status_label)
        root_layout.addWidget(summary_frame)
        root_layout.addWidget(self.video_table, 1)

    def get_filters(self) -> dict[str, str]:
        return {
            "video_type": self.type_combo.currentData(),
            "view_sort": self.view_sort_combo.currentData(),
        }

    def set_status(self, text: str):
        self.status_label.setText(text)

    def set_summary(self, lines: list[str]):
        self.summary_text.setPlainText("\n".join(lines))

    def set_videos(self, videos: list[dict]):
        self.video_table.setRowCount(len(videos))

        for row, video in enumerate(videos, start=1):
            row_values = [
                str(row),
                video.get("title", ""),
                video.get("video_id", ""),
                video.get("published_at", ""),
                video.get("duration_text", ""),
                video.get("video_type", ""),
                self._format_int(video.get("view_count", 0)),
                self._format_int(video.get("comment_count", 0)),
                video.get("url", ""),
            ]

            for col, value in enumerate(row_values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col in (1, 8):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    )
                self.video_table.setItem(row - 1, col, item)

    def clear_results(self):
        self.summary_text.clear()
        self.video_table.setRowCount(0)

    def _build_filter_frame(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("panelCard")

        layout = QGridLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(4)

        type_label = QLabel("Loại")
        type_label.setObjectName("fieldLabel")
        self.type_combo = QComboBox()
        self.type_combo.addItem("Tất cả", "")
        self.type_combo.addItem("Short", "short")
        self.type_combo.addItem("Video", "long")

        views_label = QLabel("Lượt xem")
        views_label.setObjectName("fieldLabel")
        self.view_sort_combo = QComboBox()
        self.view_sort_combo.addItem("Mặc định", "")
        self.view_sort_combo.addItem("Cao -> thấp", "views_desc")

        layout.addWidget(type_label, 0, 0)
        layout.addWidget(views_label, 0, 1)
        layout.addWidget(self.type_combo, 1, 0)
        layout.addWidget(self.view_sort_combo, 1, 1)

        return frame

    def _format_int(self, value: int) -> str:
        return f"{int(value):,}"
