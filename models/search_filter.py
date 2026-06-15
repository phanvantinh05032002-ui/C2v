from dataclasses import dataclass


@dataclass
class SearchFilter:
    keyword: str = ""
    region_code: str = ""
    published_days: int = 1
    recent_videos_limit: int = 8
    min_subscribers: int = 0
    max_subscribers: int = 2_147_483_647
    min_views: int = 0
    max_views: int = 2_147_483_647
    min_total_videos: int = 0
    min_channel_age_days: int = 0
    max_channel_age_days: int = 36_500
    max_results: int = 50
    trending_region_code: str = "JP"
