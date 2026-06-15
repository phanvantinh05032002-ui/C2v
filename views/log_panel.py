from PyQt6.QtWidgets import QTextEdit


class LogPanel(QTextEdit):

    def __init__(self):
        super().__init__()

        self.setObjectName("logPanel")
        self.setReadOnly(True)
        self.setMinimumHeight(50)
        self.setMaximumHeight(100)
        self.setPlainText(

            "Hoàn tất."
        )

    def write(self, text):
        self.append(text)
