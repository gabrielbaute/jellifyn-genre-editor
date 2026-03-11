import logging
from typing import Dict, Any
from app.schemas import Album, Artist, GenreItem, Track
class JellyfinParser:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse_artist(self, data: Dict[str, Any]) -> Artist:
        try:
            artist = Artist(
                name=data["Name"],
                server_id=data["ServerId"],
                artis_id=data["Id"],
                path=data.get("Path", ""),
                genres=data.get("Genres", []),
                tags=data.get("Tags", []),
                genre_items=[GenreItem(**item) for item in data.get("GenreItems", [])]
            )
            return artist
        except Exception as e:
            self.logger.error(f"Error al parsear artista: {e}")
            return None
        
    def parse_album(self, data: Dict[str, Any]) -> Album:
        try:
            return Album(
                name=data["Name"],
                id=data["Id"],
                server_id=data["ServerId"],
                path=data.get("Path", ""),
                genres=data.get("Genres", []),
                tags=data.get("Tags", []),
                genre_items=[GenreItem(**item) for item in data.get("GenreItems", [])]
            )
        except Exception as e:
            self.logger.error(f"Error al parsear álbum: {e}")
            return None
        

    def parse_track(self, data: Dict[str, Any]) -> Track:
        try:
            return Track(
                name=data["Name"],
                id=data["Id"],
                server_id=data["ServerId"],
                path=data.get("Path", ""),
                container=data.get("Container", "unknown"),
                genres=data.get("Genres", []),
                tags=data.get("Tags", []),
                genre_items=[GenreItem(**item) for item in data.get("GenreItems", [])],
                artists=data.get("Artists", []),
                album_name=data.get("Album", ""),
                album_id=data.get("AlbumId", ""),
                production_year=data.get("ProductionYear")
            )
        except Exception as e:
            self.logger.error(f"Error al parsear track {data.get('Name')}: {e}")
            return None