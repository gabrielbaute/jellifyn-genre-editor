from typing import List
from pydantic import BaseModel

from app.schemas.genre_item_schema import GenreItem

class Artist(BaseModel):
    name: str
    server_id: str
    artis_id: str
    path: str
    genres: List[str]
    tags: List[str]
    genre_items: List[GenreItem]
    