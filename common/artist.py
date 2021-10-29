from dataclasses import dataclass
from typing import List


@dataclass
class Artist:
    name: str
    spotify_id: str
    followers: int
    popularity: int
    genres: List[str]

