from dataclasses import dataclass


@dataclass
class SearchFilter:
    keyword: str = ""

    country: str = ""

    min_subs: int = 0
    max_subs: int = 999999999

    min_views: int = 0
    max_views: int = 999999999

    recent_days: int = 7

    max_results: int = 100
