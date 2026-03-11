from typing import List, Optional
from pydantic import BaseModel

from app.schemas.genre_item_schema import GenreItem

class Track(BaseModel):
    name: str
    id: str
    server_id: str
    path: str
    container: str  # e.g., "mp3", "flac"
    genres: List[str]
    tags: List[str]
    genre_items: List[GenreItem] = []  # Lista de objetos GenreItem
    artists: List[str]  # Lista de nombres de artistas colaboradores
    album_name: str     # Mapeado desde "Album" en el JSON
    album_id: str
    production_year: Optional[int] = None