import logging
from typing import List
from app.schemas import Album
from app.services.jellyfin_client_service import JellyfinClientService

class GenreEditor:
    """
    Orquestador para la edición masiva de géneros en Jellyfin.
    """
    def __init__(self, service: JellyfinClientService):
        """
        Args:
            service (JellyfinClientService): Instancia del servicio de conexión.
        """
        self.jf = service
        self.logger = logging.getLogger(self.__class__.__name__)

    # ============== Métodos internos ==============
    def _add_genre_to_single_track(self, track_id: str, genre: str) -> bool:
        """
        Lógica interna para obtener, modificar y subir el track.

        Args:
            track_id (str): ID del track.
            genre (str): Género a añadir.
            
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario.
        """
        # 1. Obtener JSON crudo
        raw_data = self.jf.get_raw_item(track_id)
        if not raw_data:
            return False

        # 2. Modificar solo si no existe (idempotencia)
        current_genres = raw_data.get("Genres", [])
        if genre not in current_genres:
            current_genres.append(genre)
            raw_data["Genres"] = current_genres
            
            # 3. Actualizar
            success = self.jf.update_item(track_id, raw_data)
            if success:
                self.logger.info(f"[OK] Track '{raw_data.get('Name')}': +{genre}")
                return True
        return False
    
    def _add_genre_to_an_album_item(self, item_id: str, genre: str) -> bool:
        """
        Lógica interna para obtener, modificar y subir el álbum. Se asigna el género al album en si, sin tocar los tracks.

        Args:
            item_id (str): ID del álbum.
            genre (str): Género a añadir.
        
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario.
        """
        raw_data = self.jf.get_raw_item(item_id)
        if not raw_data:
            return False
        
        current_genres = raw_data.get("Genres", [])
        if not genre in current_genres:
            current_genres.append(genre)
            raw_data["Genres"] = current_genres
            success = self.jf.update_item(item_id, raw_data)
            if success:
                self.logger.info(f"[OK] Album ':{raw_data.get('Name')}': +{genre}")
                return True
        return False
    
    def _add_genre_to_an_artist_item(self, item_id: str, genre: str) -> bool:
        """
        Lógica interna para obtener, modificar y subir el artista. Se asigna el género al artista en si, sin tocar los tracks.
        
        Args:
            item_id (str): ID del artista.
            genre (str): Género a añadir.
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario.
        """
        raw_data = self.jf.get_raw_item(item_id)
        if not raw_data:
            return False
        
        current_genres = raw_data.get("Genres", [])
        if not genre in current_genres:
            current_genres.append(genre)
            raw_data["Genres"]
            success = self.jf.update_item(item_id, raw_data)
            if success:
                self.logger.info(f"[OK] Artista {raw_data.get('Name')}': +{genre}")
                return True
        return False

    # ============== Métodos públicos ==============
    def get_albums_by_artist(self, artist_name: str) -> List[Album]:
        """
        Obtiene la lista de álbumes de un artista.
        
        Args:
            artist_name (str): Nombre del artista.
            
        Returns:
            List[Album]: Lista de álbumes.
        """
        artist = self.jf.get_artist_by_name(artist_name)
        if not artist:
            self.logger.error(f"No se encontró el artista: {artist_name}")
            return []
        return self.jf.get_items_by_artist(artist.artis_id)

    def add_gemre_to_album(self, album_id: str, genre: str) -> None:
        """
        Añade un género a un álbum específico.

        Args:
            album_id (str): ID del álbum.
            genre (str): Género a añadir.
        
        Returns:
            None
        """
        self._add_genre_to_an_album_item(album_id, genre)

    def add_genre_to_album_tracks(self, album_id: str, genre: str) -> None:
        """
        Añade un género a todos los tracks de un álbum específico.
        
        Args:
            album_id (str): ID del álbum.
            genre (str): Género a añadir.
        
        Returns:
            None
        """
        tracks = self.jf.get_tracks_by_album(album_id)
        if not tracks:
            self.logger.error(f"No se encontraron tracks para el álbum: {album_id}")
            return None
        
        self.logger.info(f"Procesando {len(tracks)} tracks del álbum: {album_id}")
        for track in tracks:
            self._add_genre_to_single_track(track.id, genre)

    def add_genre_to_all_artist_tracks(self, artist_name: str, genre: str) -> None:
        """
        Busca todos los álbumes de un artista y añade el género a cada track.

        Args:
            artist_name (str): Nombre del artista.
            genre (str): Género a añadir.
        
        Returns:
            None
        """
        albums = self.get_albums_by_artist(artist_name)
        for album in albums:
            self.logger.info(f"Procesando álbum: {album.name}")
            self.add_genre_to_album_tracks(album.id, genre)