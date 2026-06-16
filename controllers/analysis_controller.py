from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QApplication

from services.youtube_service import YoutubeService


class AnalysisController:
    API_KEY_PATH = Path(__file__).resolve().parent.parent / "data" / "api_keys.txt"

    def __init__(self, main_window):
        self.main_window = main_window
        self.analysis_panel = main_window.analysis_panel
        self.search_panel = main_window.search_panel

        self.analysis_panel.analyze_btn.clicked.connect(self.analyze_channel)

    def analyze_channel(self):
        api_keys = self.search_panel.get_api_keys() or self._load_api_keys_from_file()
        if not api_keys:
            self._set_status("Vui lòng nhập API key ở tab Tìm kênh trước.")
            return

        channel_id = self.analysis_panel.channel_id_input.text().strip()
        if not channel_id:
            self._set_status("Vui lòng nhập channel ID.")
            return

        filters = self.analysis_panel.get_filters()
        fetch_limit = 10 if self._is_default_filter(filters) else 50

        self.analysis_panel.analyze_btn.setEnabled(False)
        self.analysis_panel.clear_results()
        self._set_status("Đang phân tích kênh...")

        try:
            youtube_service = YoutubeService(api_keys)
            result = youtube_service.analyze_channel(channel_id, recent_video_limit=fetch_limit)
            filtered_videos = self._apply_filters(result["videos"], filters)
            result["videos"] = filtered_videos[:10]
            self.analysis_panel.set_summary(self._build_summary_lines(result, filters))
            self.analysis_panel.set_videos(result["videos"])
            self._set_status(f"Đã tải {len(result['videos'])} video theo bộ lọc.")
        except Exception as error:
            self._set_status(f"Lỗi phân tích: {error}")
        finally:
            self.analysis_panel.analyze_btn.setEnabled(True)
            QApplication.processEvents()

    def _apply_filters(self, videos: list[dict], filters: dict[str, str]) -> list[dict]:
        filtered = list(videos)

        video_type = filters.get("video_type", "")
        if video_type == "short":
            filtered = [
                video for video in filtered
                if video.get("video_type") == "Shorts candidate"
            ]
        elif video_type == "long":
            filtered = [
                video for video in filtered
                if video.get("video_type") == "Video dài"
            ]

        if filters.get("view_sort") == "views_desc":
            filtered.sort(
                key=lambda video: int(video.get("view_count", 0) or 0),
                reverse=True,
            )

        return filtered

    def _is_default_filter(self, filters: dict[str, str]) -> bool:
        return not filters.get("video_type") and not filters.get("view_sort")

    def _load_api_keys_from_file(self) -> list[str]:
        if not self.API_KEY_PATH.exists():
            return []
        return [
            line.strip()
            for line in self.API_KEY_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def _build_summary_lines(self, result: dict, filters: dict[str, str]) -> list[str]:
        filter_text = self._describe_filters(filters)
        return [
            f"Kênh: {result['title']}",
            f"Channel ID: {result['channel_id']}",
            f"Created: {result['created_at']} | Age: {result['age_days']:,} days",
            f"Subscribers: {result['subscribers']:,} | Total views: {result['total_views']:,} | Videos: {result['total_videos']:,}",
            f"Average views / video: {result['average_views']:,.2f}",
            f"Bộ lọc: {filter_text}",
            f"Đang hiển thị {len(result['videos'])} video.",
        ]

    def _describe_filters(self, filters: dict[str, str]) -> str:
        parts = []
        if filters.get("video_type") == "short":
            parts.append("Loại = Short")
        elif filters.get("video_type") == "long":
            parts.append("Loại = Video")

        if filters.get("view_sort") == "views_desc":
            parts.append("Lượt xem = Cao -> thấp")

        return ", ".join(parts) if parts else "Mặc định"

    def _set_status(self, text: str):
        self.analysis_panel.set_status(text)
        QApplication.processEvents()
