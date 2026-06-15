from dataclasses import dataclass


@dataclass
class Channel:
    channel_id: str
    channel_name: str
    url: str
    thumbnail_url: str
    country: str
    created_at: str
    age_days: int
    subscribers: int
    total_views: int
    total_videos: int
    recent_videos: int
    recent_views: int
    views_per_day: float
    subscribers_per_day: float
