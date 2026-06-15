from __future__ import annotations

from urllib.error import URLError
from urllib.request import urlopen

from PyQt6.QtCore import QPoint, Qt, QUrl, QSize
from PyQt6.QtGui import QAction, QDesktopServices, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHeaderView,
    QInputDialog,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
)

from models.channel import Channel


class ChannelTable(QTableWidget):

    def __init__(self):
        super().__init__()

        self.channels: list[Channel] = []
        self._thumbnail_cache: dict[str, QIcon] = {}

        self.setObjectName("channelTable")
        self.setColumnCount(13)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(36)
        self.setIconSize(QSize(28, 28))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self.setHorizontalHeaderLabels(
            [
                "Icon",
                "Tên Kênh",
                "Mã kênh",
                "URL",
                "Quốc gia",
                "Ngày tạo",
                "Tuổi kênh (ngày)",
                "Người đăng ký",
                "Tổng lượt xem",
                "Tổng video",
                "Video gần đây",
                "View/ngày",
                "Sub/ngày",
            ]
        )

        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.resizeSection(0, 44)

        self.setRowCount(0)

    def set_channels(self, channels: list[Channel]):
        self.channels = channels
        self.setRowCount(len(channels))

        for row_index, channel in enumerate(channels):
            row_data = [
                "",
                channel.channel_name,
                channel.channel_id,
                channel.url,
                channel.country,
                channel.created_at,
                self._format_int(channel.age_days),
                self._format_int(channel.subscribers),
                self._format_int(channel.total_views),
                self._format_int(channel.total_videos),
                self._format_int(channel.recent_videos),
                self._format_float(channel.views_per_day),
                self._format_float(channel.subscribers_per_day),
            ]

            for column_index, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if column_index == 0:
                    item.setIcon(self._get_thumbnail_icon(channel.thumbnail_url))
                if column_index in (1, 3):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    )
                self.setItem(row_index, column_index, item)

    def apply_text_filter(self, text: str):
        normalized = text.strip().lower()

        for row in range(self.rowCount()):
            row_text = " ".join(
                self.item(row, column).text().lower()
                for column in range(self.columnCount())
                if self.item(row, column)
            )
            self.setRowHidden(row, normalized not in row_text if normalized else False)

    def _get_thumbnail_icon(self, thumbnail_url: str) -> QIcon:
        if not thumbnail_url:
            return QIcon()

        if thumbnail_url in self._thumbnail_cache:
            return self._thumbnail_cache[thumbnail_url]

        try:
            with urlopen(thumbnail_url, timeout=10) as response:
                image_data = response.read()
        except (URLError, TimeoutError, ValueError):
            return QIcon()

        pixmap = QPixmap()
        if not pixmap.loadFromData(image_data):
            return QIcon()

        scaled = pixmap.scaled(
            28,
            28,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        icon = QIcon(scaled)
        self._thumbnail_cache[thumbnail_url] = icon
        return icon

    def _show_context_menu(self, position: QPoint):
        item = self.itemAt(position)
        if item is None:
            return

        row = item.row()
        if row >= len(self.channels):
            return

        self.selectRow(row)
        channel = self.channels[row]

        menu = QMenu(self)

        open_action = QAction("Mở kênh", self)
        open_action.triggered.connect(lambda: self._open_channel(channel.url))
        menu.addAction(open_action)

        menu.addSeparator()

        copy_id_action = QAction("Copy: Channel ID", self)
        copy_id_action.triggered.connect(lambda: self._copy_to_clipboard(channel.channel_id))
        menu.addAction(copy_id_action)

        copy_id_title_action = QAction("Copy: Channel ID | Title", self)
        copy_id_title_action.triggered.connect(
            lambda: self._copy_to_clipboard(
                f"{channel.channel_id} | {channel.channel_name}"
            )
        )
        menu.addAction(copy_id_title_action)

        copy_id_title_url_action = QAction("Copy: Channel ID | Title | URL", self)
        copy_id_title_url_action.triggered.connect(
            lambda: self._copy_to_clipboard(
                f"{channel.channel_id} | {channel.channel_name} | {channel.url}"
            )
        )
        menu.addAction(copy_id_title_url_action)

        copy_basic_action = QAction(
            "Copy: Channel ID | Title | URL | Country",
            self,
        )
        copy_basic_action.triggered.connect(
            lambda: self._copy_to_clipboard(
                f"{channel.channel_id} | {channel.channel_name} | {channel.url} | {channel.country}"
            )
        )
        menu.addAction(copy_basic_action)

        copy_stats_action = QAction(
            "Copy: Channel ID | Subs | Total Views",
            self,
        )
        copy_stats_action.triggered.connect(
            lambda: self._copy_to_clipboard(
                f"{channel.channel_id} | {channel.subscribers} | {channel.total_views}"
            )
        )
        menu.addAction(copy_stats_action)

        copy_custom_action = QAction(
            "Copy: Custom fields (nhập key ngăn cách bằng dấu phẩy)",
            self,
        )
        copy_custom_action.triggered.connect(lambda: self._copy_custom_fields(channel))
        menu.addAction(copy_custom_action)

        menu.exec(self.viewport().mapToGlobal(position))

    def _copy_custom_fields(self, channel: Channel):
        fields_text, accepted = QInputDialog.getText(
            self,
            "Copy Custom Fields",
            (
                "Nhập field, cách nhau bằng dấu phẩy.\n"
                "Ví dụ: channel_id,channel_name,url,country"
            ),
        )
        if not accepted or not fields_text.strip():
            return

        available_fields = {
            "channel_id": channel.channel_id,
            "channel_name": channel.channel_name,
            "title": channel.channel_name,
            "url": channel.url,
            "thumbnail_url": channel.thumbnail_url,
            "country": channel.country,
            "created_at": channel.created_at,
            "age_days": channel.age_days,
            "subscribers": channel.subscribers,
            "total_views": channel.total_views,
            "total_videos": channel.total_videos,
            "recent_videos": channel.recent_videos,
            "recent_views": channel.recent_views,
            "views_per_day": f"{channel.views_per_day:.2f}",
            "subscribers_per_day": f"{channel.subscribers_per_day:.2f}",
        }

        values = []
        for raw_field in fields_text.split(","):
            field = raw_field.strip().lower()
            if not field:
                continue
            values.append(str(available_fields.get(field, "")))

        if values:
            self._copy_to_clipboard(" | ".join(values))

    def _copy_to_clipboard(self, text: str):
        QApplication.clipboard().setText(text)

    def _open_channel(self, url: str):
        QDesktopServices.openUrl(QUrl(url))

    def _format_int(self, value: int) -> str:
        return f"{value:,}"

    def _format_float(self, value: float) -> str:
        return f"{value:,.2f}"
