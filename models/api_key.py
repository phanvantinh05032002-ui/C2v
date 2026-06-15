from dataclasses import dataclass


@dataclass
class ApiKey:
    key: str
    quota_used: int = 0
