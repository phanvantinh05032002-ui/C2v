
from dataclasses import dataclass


@dataclass
class Channel:
    channel_id: str
    channel_name: str
    url: str
    country: str
    created_at: str

    subscribers: int
    total_views: int
    total_videos: int

    recent_videos: int
    views_per_day: float
    views_per_video: float