from typing import List
from pydantic import BaseModel

from app.schemas.genre_item_schema import GenreItem

class Album(BaseModel):
    name: str
    id: str
    server_id: str
    path: str
    genres: List[str]
    tags: List[str]
    genre_items: List[GenreItem]