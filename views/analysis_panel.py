from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
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


class AnalysisFilterDialog(QDialog):

    def __init__(self, current_filters: dict[str, str], parent=None):
        super().__init__(parent)

        self.setWindowTitle("Bộ lọc tìm kiếm")
        self.setModal(True)
        self.resize(560, 220)
        self.setObjectName("filterDialog")

        self.selected_filters = dict(current_filters)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(12)

        title_row = QHBoxLayout()
        title_label = QLabel("Bộ lọc tìm kiếm")
        title_label.setObjectName("dialogTitle")

        close_btn = QPushButton("✕")
        close_btn.setObjectName("dialogCloseButton")
        close_btn.clicked.connect(self.reject)

        title_row.addWidget(title_label)
        title_row.addStretch(1)
        title_row.addWidget(close_btn)

        filter_grid = QGridLayout()
        filter_grid.setHorizontalSpacing(20)
        filter_grid.setVerticalSpacing(10)

        type_title = QLabel("LOẠI")
        type_title.setObjectName("dialogSectionTitle")
        views_title = QLabel("LƯỢT XEM")
        views_title.setObjectName("dialogSectionTitle")

        filter_grid.addWidget(type_title, 0, 0)
        filter_grid.addWidget(views_title, 0, 1)

        self.type_all_btn = self._create_option_button("Tất cả", "type", "")
        self.type_short_btn = self._create_option_button("Shorts", "type", "short")
        self.type_video_btn = self._create_option_button("Video", "type", "long")

        self.views_default_btn = self._create_option_button("Mặc định", "views", "")
        self.views_desc_btn = self._create_option_button(
            "Cao -> thấp",
            "views",
            "views_desc",
        )

        type_col = QVBoxLayout()
        type_col.setSpacing(8)
        type_col.addWidget(self.type_all_btn)
        type_col.addWidget(self.type_short_btn)
        type_col.addWidget(self.type_video_btn)
        type_col.addStretch(1)

        views_col = QVBoxLayout()
        views_col.setSpacing(8)
        views_col.addWidget(self.views_default_btn)
        views_col.addWidget(self.views_desc_btn)
        views_col.addStretch(1)

        filter_grid.addLayout(type_col, 1, 0)
        filter_grid.addLayout(views_col, 1, 1)

        action_row = QHBoxLayout()
        action_row.addStretch(1)

        reset_btn = QPushButton("Đặt lại")
        reset_btn.setObjectName("secondaryButton")
        reset_btn.clicked.connect(self._reset_filters)

        apply_btn = QPushButton("Áp dụng")
        apply_btn.setObjectName("primaryButton")
        apply_btn.clicked.connect(self.accept)

        action_row.addWidget(reset_btn)
        action_row.addWidget(apply_btn)

        root_layout.addLayout(title_row)
        root_layout.addLayout(filter_grid)
        root_layout.addStretch(1)
        root_layout.addLayout(action_row)

        self._refresh_button_states()

    def get_filters(self) -> dict[str, str]:
        return dict(self.selected_filters)

    def _create_option_button(self, text: str, group: str, value: str) -> QPushButton:
        button = QPushButton(text)
        button.setCheckable(True)
        button.setObjectName("dialogOptionButton")
        button.clicked.connect(lambda checked=False, g=group, v=value: self._select(g, v))
        return button

    def _select(self, group: str, value: str):
        if group == "type":
            self.selected_filters["video_type"] = value
        elif group == "views":
            self.selected_filters["view_sort"] = value
        self._refresh_button_states()

    def _reset_filters(self):
        self.selected_filters = {
            "video_type": "",
            "view_sort": "",
        }
        self._refresh_button_states()

    def _refresh_button_states(self):
        current_type = self.selected_filters.get("video_type", "")
        current_views = self.selected_filters.get("view_sort", "")

        self.type_all_btn.setChecked(current_type == "")
        self.type_short_btn.setChecked(current_type == "short")
        self.type_video_btn.setChecked(current_type == "long")

        self.views_default_btn.setChecked(current_views == "")
        self.views_desc_btn.setChecked(current_views == "views_desc")


class AnalysisPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.filters = {
            "video_type": "",
            "view_sort": "",
        }

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Kênh:"))

        self.channel_id_input = QLineEdit()
        self.channel_id_input.setPlaceholderText("Nhập channel ID...")
        top_row.addWidget(self.channel_id_input, 1)

        self.filter_btn = QPushButton("Bộ lọc")
        self.filter_btn.setObjectName("secondaryButton")
        self.filter_btn.clicked.connect(self.open_filter_dialog)
        top_row.addWidget(self.filter_btn)

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

        self._update_filter_button_text()

    def get_filters(self) -> dict[str, str]:
        return dict(self.filters)

    def open_filter_dialog(self):
        dialog = AnalysisFilterDialog(self.filters, self)
        if dialog.exec():
            self.filters = dialog.get_filters()
            self._update_filter_button_text()

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

    def _update_filter_button_text(self):
        parts = []
        if self.filters.get("video_type") == "short":
            parts.append("Short")
        elif self.filters.get("video_type") == "long":
            parts.append("Video")

        if self.filters.get("view_sort") == "views_desc":
            parts.append("Views")

        self.filter_btn.setText(
            "Bộ lọc" if not parts else f"Bộ lọc ({', '.join(parts)})"
        )

    def _format_int(self, value: int) -> str:
        return f"{int(value):,}"
