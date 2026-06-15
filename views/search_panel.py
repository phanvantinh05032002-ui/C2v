from __future__ import annotations

import unicodedata

from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from models.search_filter import SearchFilter
from views.account_info import AccountInfoBar


class SearchPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("searchPanel")

        self.account_info = AccountInfoBar()

        self.api_keys_edit = QPlainTextEdit()
        self.api_keys_edit.setObjectName("apiKeysEdit")
        self.api_keys_edit.setPlainText(
            "AIzaSyYourKey01\nAIzaSyYourKey02\nAIzaSyYourKey03"
        )

        self.save_api_btn = QPushButton("Lưu API")
        self.save_api_btn.setObjectName("primaryButton")

        self.keyword_input = QLineEdit("2ch")
        self.country_combo = QComboBox()
        self.country_combo.setEditable(True)
        self.country_combo.addItems(
            ["", "JP", "US", "GB", "VN", "FR", "KR", "DE", "BR", "MX"]
        )
        self.country_combo.setCurrentText("JP")

        self.recent_videos_spin = self._build_spin_box(0, 9999, 8)
        self.max_results_spin = self._build_spin_box(1, 1000, 150)
        self.published_days_spin = self._build_spin_box(0, 3650, 1)
        self.channel_age_min_spin = self._build_spin_box(0, 36500, 0)
        self.channel_age_max_spin = self._build_spin_box(0, 36500, 18250)
        self.worker_threads_spin = self._build_spin_box(1, 64, 5)

        self.min_sub_input = QLineEdit("0")
        self.max_sub_input = QLineEdit("2147483647")
        self.min_views_input = QLineEdit("0")
        self.max_views_input = QLineEdit("2147483647")
        self.min_total_videos_input = QLineEdit("0")

        self.trending_combo = QComboBox()
        self.trending_combo.addItems(["JP", "US", "GB", "VN"])

        self.help_btn = QPushButton("?")
        self.help_btn.setObjectName("helpButton")
        self.help_btn.setFixedWidth(28)

        self.start_btn = QPushButton("Bắt đầu tìm")
        self.start_btn.setObjectName("accentButton")

        self.stop_btn = QPushButton("Dừng")
        self.stop_btn.setObjectName("secondaryButton")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(6)

        main_layout.addWidget(self.account_info)
        main_layout.addWidget(self._build_api_section())
        main_layout.addWidget(self._build_filter_section())

    def get_api_keys(self) -> list[str]:
        return [
            line.strip()
            for line in self.api_keys_edit.toPlainText().splitlines()
            if line.strip()
        ]

    def set_api_keys(self, api_keys: str):
        self.api_keys_edit.setPlainText(api_keys)

    def to_search_filter(self) -> SearchFilter:
        region_code = self._resolve_region_code(self.country_combo.currentText())
        trending_region = self._resolve_region_code(self.trending_combo.currentText()) or "JP"

        return SearchFilter(
            keyword=self.keyword_input.text().strip(),
            region_code=region_code,
            published_days=self.published_days_spin.value(),
            recent_videos_limit=self.recent_videos_spin.value(),
            min_subscribers=self._parse_int(self.min_sub_input.text(), 0),
            max_subscribers=self._parse_int(
                self.max_sub_input.text(),
                2_147_483_647,
            ),
            min_views=self._parse_int(self.min_views_input.text(), 0),
            max_views=self._parse_int(
                self.max_views_input.text(),
                2_147_483_647,
            ),
            min_total_videos=self._parse_int(self.min_total_videos_input.text(), 0),
            min_channel_age_days=self.channel_age_min_spin.value(),
            max_channel_age_days=self.channel_age_max_spin.value(),
            max_results=self.max_results_spin.value(),
            trending_region_code=trending_region,
        )

    def _build_api_section(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("panelCard")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        label = QLabel("API Keys (mỗi dòng 1 key):")
        label.setObjectName("sectionLabel")

        layout.addWidget(label, 2)
        layout.addWidget(self.api_keys_edit, 8)
        layout.addWidget(self.save_api_btn, 1)

        return frame

    def _build_filter_section(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("panelCard")

        outer_layout = QVBoxLayout(frame)
        outer_layout.setContentsMargins(8, 8, 8, 8)
        outer_layout.setSpacing(8)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(5, 1)

        self._add_field(
            grid,
            0,
            0,
            "Từ khóa (để trống nếu TOP TRENDING):",
            self.keyword_input,
        )
        self._add_field(
            grid,
            0,
            2,
            "Khu vực (US,GB,JP... | rỗng = global):",
            self.country_combo,
        )
        self._add_field(
            grid,
            0,
            4,
            "Video đăng trong (ngày):",
            self.published_days_spin,
        )

        self._add_field(
            grid,
            1,
            0,
            "Video gần đây / kênh:",
            self.recent_videos_spin,
        )
        self._add_field(
            grid,
            1,
            2,
            "Kết quả tối đa / từ khóa:",
            self.max_results_spin,
        )
        self._add_field(
            grid,
            1,
            4,
            "Tối thiểu sub:",
            self.min_sub_input,
        )

        self._add_field(
            grid,
            2,
            0,
            "Tối đa sub:",
            self.max_sub_input,
        )
        self._add_field(
            grid,
            2,
            2,
            "Tối thiểu lượt xem:",
            self.min_views_input,
        )
        self._add_field(
            grid,
            2,
            4,
            "Tối đa lượt xem:",
            self.max_views_input,
        )

        self._add_field(
            grid,
            3,
            0,
            "Tuổi kênh tối thiểu (ngày):",
            self.channel_age_min_spin,
        )
        self._add_field(
            grid,
            3,
            2,
            "Tuổi kênh tối đa (ngày):",
            self.channel_age_max_spin,
        )
        self._add_field(
            grid,
            3,
            4,
            "Tối thiểu tổng video:",
            self.min_total_videos_input,
        )

        self._add_field(
            grid,
            4,
            0,
            "Số luồng xử lý:",
            self.worker_threads_spin,
        )

        trending_row = QHBoxLayout()
        trending_row.setSpacing(6)
        trending_row.addWidget(QLabel("TOP TRENDING (theo quốc gia)"))
        trending_row.addWidget(self.help_btn)
        trending_row.addWidget(self.trending_combo)
        trending_row.addStretch(1)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        action_row.addWidget(self.start_btn)
        action_row.addWidget(self.stop_btn)
        action_row.addStretch(1)

        outer_layout.addLayout(grid)
        outer_layout.addLayout(trending_row)
        outer_layout.addLayout(action_row)

        return frame

    def _add_field(self, layout, row, col, label_text, field):
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label, row, col)
        layout.addWidget(field, row, col + 1)

    def _build_spin_box(self, minimum, maximum, value):
        spin_box = QSpinBox()
        spin_box.setRange(minimum, maximum)
        spin_box.setValue(value)
        return spin_box

    def _resolve_region_code(self, value: str) -> str:
        normalized = self._strip_accents(value.strip().upper())
        aliases = {
            "": "",
            "GLOBAL": "",
            "US": "US",
            "USA": "US",
            "HOA KY": "US",
            "GB": "GB",
            "UK": "GB",
            "ANH": "GB",
            "JP": "JP",
            "NHAT BAN": "JP",
            "VN": "VN",
            "VIET NAM": "VN",
            "FR": "FR",
            "PHAP": "FR",
            "KR": "KR",
            "HAN QUOC": "KR",
            "DE": "DE",
            "DUC": "DE",
            "BR": "BR",
            "BRAZIL": "BR",
            "MX": "MX",
            "MEXICO": "MX",
        }
        return aliases.get(normalized, normalized if len(normalized) == 2 else "")

    def _strip_accents(self, value: str) -> str:
        normalized = unicodedata.normalize("NFD", value)
        return "".join(
            character
            for character in normalized
            if unicodedata.category(character) != "Mn"
        ).replace("Đ", "D")

    def _parse_int(self, value: str, default: int) -> int:
        try:
            return int(value.strip() or default)
        except ValueError:
            return default
