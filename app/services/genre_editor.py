import logging
from typing import List
from app.schemas import Album, EditResult
from app.enums import ItemType, EditStatus
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

    # ============== Métodos internos (Atómicos) ==============
    def _update_item_genre(self, item_id: str, genre: str, item_type_label: ItemType) -> EditStatus:
        """
        Método atómico genérico para actualizar el género de cualquier ítem.

        Args:
            item_id (str): ID del ítem.
            genre (str): Género a añadir.
            item_type_label (ItemType): Etiqueta del tipo de ítem.
            
        Returns:
            EditStatus: Estado de edición.
        """
        raw_data = self.jf.get_raw_item(item_id)
        if not raw_data:
            self.logger.error(f"No se pudo obtener el ítem {item_id}")
            return EditStatus.ERROR

        name = raw_data.get("Name", "Unknown")
        current_genres = raw_data.get("Genres", [])

        if genre not in current_genres:
            current_genres.append(genre)
            raw_data["Genres"] = current_genres
            
            success = self.jf.update_item(item_id, raw_data)
            if success:
                self.logger.info(f"[OK] {item_type_label.value} '{name}': +{genre}")
                return EditStatus.UPDATED
            return EditStatus.ERROR
            
        return EditStatus.SKIPPED

    def _add_genre_to_single_track(self, track_id: str, genre: str) -> EditStatus:
        return self._update_item_genre(track_id, genre, ItemType.TRACK)

    def _add_genre_to_an_album_item(self, item_id: str, genre: str) -> EditStatus:
        return self._update_item_genre(item_id, genre, ItemType.ALBUM)

    def _add_genre_to_an_artist_item(self, item_id: str, genre: str) -> EditStatus:
        return self._update_item_genre(item_id, genre, ItemType.ARTIST)

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

    def add_genre_to_album(self, album_id: str, genre: str) -> EditResult:
        """
        Añade género al álbum y devuelve el resultado para el reporte.
        
        Args:
            album_id (str): ID del álbum.
            genre (str): Género a añadir.
            
        Returns:
            EditResult: Resultado de la edición.
        """
        # Obtenemos el nombre antes para el resultado si es posible, 
        # o dejamos que el método atómico haga su magia.
        status = self._add_genre_to_an_album_item(album_id, genre)
        return EditResult(name=album_id, item_type=ItemType.ALBUM, status=status)

    def add_genre_to_album_tracks(self, album_id: str, genre: str) -> List[EditResult]:
        """
        ñade género a tracks y construye la lista de resultados.

        Args:
            album_id (str): ID del álbum.
            genre (str): Género a añadir.
            
        Returns:
            List[EditResult]: Lista de resultados de edición.
        """
        results = []
        tracks = self.jf.get_tracks_by_album(album_id)
        
        if not tracks:
            return [EditResult(name=album_id, item_type=ItemType.ALBUM, status=EditStatus.ERROR, message="No tracks found")]

        for track in tracks:
            status = self._add_genre_to_single_track(track.id, genre)
            results.append(EditResult(name=track.name, item_type=ItemType.TRACK, status=status))
            
        return results

    def add_genre_to_all_artist_tracks(self, artist_name: str, genre: str) -> List[EditResult]:
        """
        Orquestador de alto nivel para todo un artista.
        
        Args:
            artist_name (str): Nombre del artista.
            genre (str): Género a añadir.
            
        Returns:
            List[EditResult]: Lista de resultados de edición.
        """
        all_results = []
        albums = self.get_albums_by_artist(artist_name)
        
        for album in albums:
            self.logger.info(f"Procesando álbum: {album.name}")
            album_results = self.add_genre_to_album_tracks(album.id, genre)
            all_results.extend(album_results)
            
        return all_results