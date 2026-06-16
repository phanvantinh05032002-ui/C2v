from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from models.channel import Channel
from models.search_filter import SearchFilter


class YoutubeService:

    def __init__(self, api_keys: list[str]):
        self.api_keys = [key.strip() for key in api_keys if key.strip()]
        self._client_index = 0
        self.youtube = self._build_client()

    def search_channels(
        self,
        search_filter: SearchFilter,
        logger: Callable[[str], None] | None = None,
        should_continue: Callable[[], bool] | None = None,
    ) -> list[Channel]:
        log = logger or (lambda message: None)
        can_continue = should_continue or (lambda: True)

        if not self.api_keys:
            raise ValueError("Chưa có API key hợp lệ.")

        if search_filter.keyword.strip():
            channel_ids = self._search_channel_ids(search_filter, log, can_continue)
        else:
            channel_ids = self._search_trending_channel_ids(
                search_filter,
                log,
                can_continue,
            )

        if not channel_ids:
            return []

        channels = self._fetch_channels(channel_ids)
        published_after = self._get_published_after(search_filter.published_days)
        results: list[Channel] = []

        for index, channel_data in enumerate(channels, start=1):
            if not can_continue():
                log("Đã dừng tìm kiếm theo yêu cầu.")
                break

            channel = self._build_channel(channel_data, search_filter, published_after)
            if channel and self._passes_filters(channel, search_filter):
                results.append(channel)

            log(f"Đã phân tích {index}/{len(channels)} kênh...")

        return results

    def analyze_channel(self, channel_id: str, recent_video_limit: int = 10) -> dict:
        channel_response = self._execute(
            lambda youtube: youtube.channels().list(
                part="contentDetails,snippet,statistics",
                id=channel_id,
            )
        )
        items = channel_response.get("items", [])
        if not items:
            raise ValueError("Không tìm thấy channel với ID đã nhập.")

        channel_data = items[0]
        snippet = channel_data.get("snippet", {})
        statistics = channel_data.get("statistics", {})
        uploads_playlist_id = (
            channel_data.get("contentDetails", {})
            .get("relatedPlaylists", {})
            .get("uploads", "")
        )
        if not uploads_playlist_id:
            raise ValueError("Không lấy được uploads playlist của kênh.")

        videos = self._fetch_playlist_videos(uploads_playlist_id, recent_video_limit)
        total_views = int(statistics.get("viewCount", 0) or 0)
        total_videos = int(statistics.get("videoCount", 0) or 0)
        subscribers = int(statistics.get("subscriberCount", 0) or 0)
        published_at = self._parse_datetime(snippet.get("publishedAt", ""))
        age_days = max((datetime.now(timezone.utc) - published_at).days, 1)

        return {
            "channel_id": channel_id,
            "title": snippet.get("title", ""),
            "created_at": published_at.date().isoformat(),
            "age_days": age_days,
            "subscribers": subscribers,
            "total_views": total_views,
            "total_videos": total_videos,
            "average_views": total_views / total_videos if total_videos else 0,
            "thumbnail_url": self._get_thumbnail_url(snippet.get("thumbnails", {})),
            "videos": videos,
        }

    def _build_client(self):
        return build(
            "youtube",
            "v3",
            developerKey=self.api_keys[self._client_index],
            cache_discovery=False,
        )

    def _execute(self, request_factory: Callable):
        last_error = None

        for _ in range(len(self.api_keys)):
            try:
                request = request_factory(self.youtube)
                return request.execute()
            except HttpError as error:
                last_error = error
                if not self._should_rotate_key(error):
                    raise
                self._rotate_key()

        if last_error is not None:
            raise last_error
        raise RuntimeError("Không thể thực thi request YouTube.")

    def _should_rotate_key(self, error: HttpError) -> bool:
        status = getattr(error.resp, "status", None)
        if status not in (400, 403):
            return False

        message = ""
        if hasattr(error, "content") and error.content:
            message = error.content.decode("utf-8", errors="ignore").lower()

        return "quota" in message or "key" in message or "forbidden" in message

    def _rotate_key(self):
        self._client_index = (self._client_index + 1) % len(self.api_keys)
        self.youtube = self._build_client()

    def _search_channel_ids(
        self,
        search_filter: SearchFilter,
        logger: Callable[[str], None],
        should_continue: Callable[[], bool],
    ) -> list[str]:
        channel_ids: list[str] = []
        seen_ids: set[str] = set()
        next_page_token = None

        while len(channel_ids) < search_filter.max_results and should_continue():
            remaining = min(50, search_filter.max_results - len(channel_ids))

            def request_factory(youtube):
                request_kwargs = {
                    "part": "snippet",
                    "q": search_filter.keyword,
                    "type": "channel",
                    "maxResults": remaining,
                }
                if search_filter.region_code:
                    request_kwargs["regionCode"] = search_filter.region_code
                if next_page_token:
                    request_kwargs["pageToken"] = next_page_token
                return youtube.search().list(**request_kwargs)

            response = self._execute(request_factory)

            for item in response.get("items", []):
                channel_id = item.get("snippet", {}).get("channelId")
                if channel_id and channel_id not in seen_ids:
                    seen_ids.add(channel_id)
                    channel_ids.append(channel_id)

            next_page_token = response.get("nextPageToken")
            logger(f"Đã lấy {len(channel_ids)} kênh từ search.list.")

            if not next_page_token:
                break

        return channel_ids[: search_filter.max_results]

    def _search_trending_channel_ids(
        self,
        search_filter: SearchFilter,
        logger: Callable[[str], None],
        should_continue: Callable[[], bool],
    ) -> list[str]:
        channel_ids: list[str] = []
        seen_ids: set[str] = set()
        next_page_token = None
        region_code = search_filter.trending_region_code or search_filter.region_code or "US"

        while len(channel_ids) < search_filter.max_results and should_continue():
            remaining = min(50, search_filter.max_results - len(channel_ids))

            def request_factory(youtube):
                request_kwargs = {
                    "part": "snippet",
                    "chart": "mostPopular",
                    "regionCode": region_code,
                    "maxResults": remaining,
                }
                if next_page_token:
                    request_kwargs["pageToken"] = next_page_token
                return youtube.videos().list(**request_kwargs)

            response = self._execute(request_factory)

            for item in response.get("items", []):
                channel_id = item.get("snippet", {}).get("channelId")
                if channel_id and channel_id not in seen_ids:
                    seen_ids.add(channel_id)
                    channel_ids.append(channel_id)

            next_page_token = response.get("nextPageToken")
            logger(f"Đã lấy {len(channel_ids)} kênh từ TOP TRENDING {region_code}.")

            if not next_page_token:
                break

        return channel_ids[: search_filter.max_results]

    def _fetch_channels(self, channel_ids: Iterable[str]) -> list[dict]:
        results: list[dict] = []
        channel_ids = list(channel_ids)

        for start in range(0, len(channel_ids), 50):
            batch = channel_ids[start : start + 50]
            response = self._execute(
                lambda youtube: youtube.channels().list(
                    part="snippet,statistics",
                    id=",".join(batch),
                )
            )
            results.extend(response.get("items", []))

        return results

    def _build_channel(
        self,
        channel_data: dict,
        search_filter: SearchFilter,
        published_after: str | None,
    ) -> Channel | None:
        snippet = channel_data.get("snippet", {})
        statistics = channel_data.get("statistics", {})
        channel_id = channel_data.get("id")

        if not channel_id:
            return None

        published_at = snippet.get("publishedAt", "")
        created_at = self._parse_datetime(published_at)
        age_days = max((datetime.now(timezone.utc) - created_at).days, 1)

        recent_videos = self._fetch_recent_videos(
            channel_id,
            search_filter.recent_videos_limit,
            published_after,
        )
        total_recent_views = sum(video["view_count"] for video in recent_videos)

        total_views = int(statistics.get("viewCount", 0) or 0)
        subscribers = int(statistics.get("subscriberCount", 0) or 0)
        total_videos = int(statistics.get("videoCount", 0) or 0)

        return Channel(
            channel_id=channel_id,
            channel_name=snippet.get("title", ""),
            url=f"https://www.youtube.com/channel/{channel_id}",
            thumbnail_url=self._get_thumbnail_url(snippet.get("thumbnails", {})),
            country=snippet.get("country", search_filter.region_code or "GLOBAL"),
            created_at=created_at.date().isoformat(),
            age_days=age_days,
            subscribers=subscribers,
            total_views=total_views,
            total_videos=total_videos,
            recent_videos=len(recent_videos),
            recent_views=total_recent_views,
            views_per_day=total_views / age_days,
            subscribers_per_day=subscribers / age_days,
        )

    def _get_thumbnail_url(self, thumbnails: dict) -> str:
        for key in ("default", "medium", "high"):
            thumbnail = thumbnails.get(key)
            if thumbnail and thumbnail.get("url"):
                return thumbnail["url"]
        return ""

    def _fetch_recent_videos(
        self,
        channel_id: str,
        video_limit: int,
        published_after: str | None,
    ) -> list[dict]:
        if video_limit <= 0:
            return []

        video_items: list[dict] = []
        next_page_token = None

        while len(video_items) < video_limit:
            remaining = min(50, video_limit - len(video_items))

            def request_factory(youtube):
                request_kwargs = {
                    "part": "id,snippet",
                    "channelId": channel_id,
                    "type": "video",
                    "order": "date",
                    "maxResults": remaining,
                }
                if published_after:
                    request_kwargs["publishedAfter"] = published_after
                if next_page_token:
                    request_kwargs["pageToken"] = next_page_token
                return youtube.search().list(**request_kwargs)

            response = self._execute(request_factory)
            items = response.get("items", [])
            if not items:
                break

            video_ids = [
                item.get("id", {}).get("videoId")
                for item in items
                if item.get("id", {}).get("videoId")
            ]
            statistics_map = self._fetch_video_statistics(video_ids)

            for item in items:
                video_id = item.get("id", {}).get("videoId")
                if not video_id:
                    continue
                video_items.append(
                    {
                        "video_id": video_id,
                        "view_count": statistics_map.get(video_id, 0),
                    }
                )
                if len(video_items) >= video_limit:
                    break

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return video_items

    def _fetch_playlist_videos(self, playlist_id: str, limit: int) -> list[dict]:
        response = self._execute(
            lambda youtube: youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=min(limit, 50),
            )
        )

        items = response.get("items", [])[:limit]
        video_ids = [
            item.get("contentDetails", {}).get("videoId")
            for item in items
            if item.get("contentDetails", {}).get("videoId")
        ]
        video_detail_map = self._fetch_video_detail_statistics(video_ids)

        videos = []
        for item in items:
            snippet = item.get("snippet", {})
            video_id = item.get("contentDetails", {}).get("videoId")
            if not video_id:
                continue
            detail = video_detail_map.get(video_id, {})
            statistics = detail.get("statistics", {})
            content_details = detail.get("contentDetails", {})
            duration_seconds = self._parse_duration_to_seconds(
                content_details.get("duration", "")
            )
            videos.append(
                {
                    "video_id": video_id,
                    "title": snippet.get("title", ""),
                    "published_at": self._parse_datetime(
                        snippet.get("publishedAt", "")
                    ).date().isoformat(),
                    "duration_seconds": duration_seconds,
                    "duration_text": self._format_duration(duration_seconds),
                    "video_type": self._classify_video_type(duration_seconds),
                    "view_count": int(statistics.get("viewCount", 0) or 0),
                    "comment_count": int(statistics.get("commentCount", 0) or 0),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )

        return videos

    def _fetch_video_statistics(self, video_ids: list[str]) -> dict[str, int]:
        if not video_ids:
            return {}

        response = self._execute(
            lambda youtube: youtube.videos().list(
                part="statistics",
                id=",".join(video_ids),
            )
        )

        statistics_map: dict[str, int] = {}
        for item in response.get("items", []):
            video_id = item.get("id")
            if not video_id:
                continue
            statistics_map[video_id] = int(
                item.get("statistics", {}).get("viewCount", 0) or 0
            )

        return statistics_map

    def _fetch_video_detail_statistics(self, video_ids: list[str]) -> dict[str, dict]:
        if not video_ids:
            return {}

        response = self._execute(
            lambda youtube: youtube.videos().list(
                part="statistics,contentDetails",
                id=",".join(video_ids),
            )
        )

        result: dict[str, dict] = {}
        for item in response.get("items", []):
            video_id = item.get("id")
            if not video_id:
                continue
            result[video_id] = {
                "statistics": item.get("statistics", {}),
                "contentDetails": item.get("contentDetails", {}),
            }
        return result

    def _parse_duration_to_seconds(self, duration: str) -> int:
        if not duration:
            return 0

        hours = 0
        minutes = 0
        seconds = 0
        current_number = ""

        for character in duration:
            if character.isdigit():
                current_number += character
                continue

            if character in ("P", "T"):
                continue

            if not current_number:
                continue

            value = int(current_number)
            current_number = ""

            if character == "H":
                hours = value
            elif character == "M":
                minutes = value
            elif character == "S":
                seconds = value

        return (hours * 3600) + (minutes * 60) + seconds

    def _format_duration(self, duration_seconds: int) -> str:
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    def _classify_video_type(self, duration_seconds: int) -> str:
        if duration_seconds <= 180:
            return "Shorts candidate"
        return "Video dài"

    def _passes_filters(self, channel: Channel, search_filter: SearchFilter) -> bool:
        if channel.subscribers < search_filter.min_subscribers:
            return False
        if channel.subscribers > search_filter.max_subscribers:
            return False
        if channel.recent_views < search_filter.min_views:
            return False
        if channel.recent_views > search_filter.max_views:
            return False
        if channel.total_videos < search_filter.min_total_videos:
            return False
        if channel.age_days < search_filter.min_channel_age_days:
            return False
        if channel.age_days > search_filter.max_channel_age_days:
            return False
        return True

    def _get_published_after(self, published_days: int) -> str | None:
        if published_days <= 0:
            return None

        published_after = datetime.now(timezone.utc) - timedelta(days=published_days)
        return published_after.replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _parse_datetime(self, value: str) -> datetime:
        if not value:
            return datetime.now(timezone.utc)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
