from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem


class ChannelTable(QTableWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("channelTable")
        self.setColumnCount(13)
        self.setRowCount(5)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(28)

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

        self._load_demo_rows()

    def _load_demo_rows(self):
        rows = [
            ["●", "おもしろch", "UCP4_Y...", "@channelalpha", "JP", "2022-03-22", "1303.8", "75300", "366737786", "341", "8", "258092.52", "7117.50"],
            ["●", "解説2ch", "UCzd57...", "@b92ch", "JP", "2011-04-19", "5283.4", "5", "1188", "107", "8", "2.54", "7.55"],
            ["●", "波音ラジオ", "UCTX5...", "@radio365", "JP", "2023-11-26", "689.7", "3270", "2228309", "346", "8", "273.93", "690.16"],
            ["●", "ほぐしch", "UCRn7...", "@relaxing", "JP", "2024-08-16", "425.7", "13800", "1612939", "72", "8", "3231.40", "6579.74"],
            ["●", "chc-tv", "UClop...", "@chc-ch9", "JP", "2022-04-30", "1264.4", "54300", "334798210", "19386", "8", "26433.60", "65735.40"],
        ]

        for row_index, row_data in enumerate(rows):
            for column_index, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if column_index in (1, 3):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    )
                self.setItem(row_index, column_index, item)
