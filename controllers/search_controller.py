from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QApplication

from services.youtube_service import YoutubeService


class SearchController:
    API_KEY_PATH = Path(__file__).resolve().parent.parent / "data" / "api_keys.txt"

    def __init__(self, main_window):
        self.main_window = main_window
        self.search_panel = main_window.search_panel
        self.table = main_window.table
        self.log_panel = main_window.log_panel
        self.table_filter_input = main_window.table_filter_input
        self._should_continue = True
        self.current_results = []

        self._load_saved_api_keys()

        self.search_panel.start_btn.clicked.connect(self.search)
        self.search_panel.stop_btn.clicked.connect(self.stop_search)
        self.search_panel.save_api_btn.clicked.connect(self.save_api_keys)
        self.table_filter_input.textChanged.connect(self.apply_table_filter)

    def search(self):
        api_keys = self.search_panel.get_api_keys()
        if not api_keys:
            self._log("Vui lòng nhập ít nhất 1 API key.")
            return

        youtube_service = YoutubeService(api_keys)
        search_filter = self.search_panel.to_search_filter()

        self._should_continue = True
        self.search_panel.start_btn.setEnabled(False)
        self.log_panel.clear()
        self._log("Bắt đầu tìm kiếm...")

        try:
            results = youtube_service.search_channels(
                search_filter,
                logger=self._log,
                should_continue=lambda: self._should_continue,
            )
            self.current_results = results
            self.table.set_channels(results)
            self.apply_table_filter(self.table_filter_input.text())
            self._log(f"Hoàn tất. Tìm thấy {len(results)} kênh phù hợp.")
        except Exception as error:
            self._log(f"Lỗi khi tìm kiếm: {error}")
        finally:
            self.search_panel.start_btn.setEnabled(True)

    def stop_search(self):
        self._should_continue = False
        self._log("Đang yêu cầu dừng tìm kiếm...")

    def save_api_keys(self):
        api_keys = self.search_panel.get_api_keys()
        self.API_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.API_KEY_PATH.write_text("\n".join(api_keys), encoding="utf-8")
        self._log(f"Đã lưu {len(api_keys)} API key.")

    def apply_table_filter(self, text: str):
        self.table.apply_text_filter(text)

    def _load_saved_api_keys(self):
        if not self.API_KEY_PATH.exists():
            return
        saved_keys = self.API_KEY_PATH.read_text(encoding="utf-8").strip()
        if saved_keys:
            self.search_panel.set_api_keys(saved_keys)

    def _log(self, message: str):
        self.log_panel.append(message)
        QApplication.processEvents()
