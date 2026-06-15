from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)


class AccountInfoBar(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("accountInfoBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # self.user_label = QLabel("👤 maychinh123 |")
        # self.user_label.setObjectName("statusChip")

        # self.expiry_label = QLabel("🗓 Hết hạn: 2025-11-09 18:52:24 |")
        # self.expiry_label.setObjectName("statusChip")

        # self.credit_label = QLabel("👑 Còn: 24 ngày")
        # self.credit_label.setObjectName("statusChip")

        self.language_label = QLabel("Ngôn ngữ:")
        self.language_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
        )

        self.language_combo = QComboBox()
        self.language_combo.addItems(["Tiếng Việt", "English"])
        self.language_combo.setCurrentText("Tiếng Việt")
        self.language_combo.setObjectName("compactCombo")

        # self.logout_btn = QPushButton("Đăng xuất")
        # self.logout_btn.setObjectName("secondaryButton")
        # self.logout_btn.setSizePolicy(
        #     QSizePolicy.Policy.Fixed,
        #     QSizePolicy.Policy.Fixed,
        # )

        # layout.addWidget(self.user_label)
        # layout.addWidget(self.expiry_label)
        # layout.addWidget(self.credit_label)
        layout.addStretch(1)
        layout.addWidget(self.language_label)
        layout.addWidget(self.language_combo)
        # layout.addWidget(self.logout_btn)
