import logging
from typing import List, Optional, Callable

from app.enums import EditStatus, ItemType
from app.schemas import EditTask, EditResult
from app.errors import ApiError, ValidationError, GenreEditorError
from app.services.jellyfin_client_service import JellyfinClientService

class GenreEditorCLI:
    """
    Orquestador para la edición masiva de géneros en Jellyfin desde la CLI con callback.
    """
    def __init__(self, service: JellyfinClientService):
        """
        Args:
            service (JellyfinClientService): Instancia del servicio de conexión.
        """
        self.jf = service
        self.logger = logging.getLogger(self.__class__.__name__)

    def build_task_list(
        self, 
        artist_name: Optional[str] = None, 
        album_id: Optional[str] = None, 
        track_id: Optional[str] = None, 
        recursive: bool = False
    ) -> List[EditTask]:
        """
        Construye el mapa de trabajo analizando la jerarquía de Jellyfin. No realiza cambios, solo recolecta metadatos.

        Args:
            artist_name (Optional[str]): Nombre del artista.
            album_id (Optional[str]): ID del álbum.
            track_id (Optional[str]): ID del track.

        Returns:
            List[EditTask]: Lista de tareas.
        """
        tasks: List[EditTask] = []

        # Caso 1: Flujo desde Artista
        if artist_name:
            self.logger.info(f"Iniciando recolección para artista: {artist_name}")
            artist = self.jf.get_artist_by_name(artist_name)
            
            if not artist:
                self.logger.error(f"Artista {artist_name} no encontrado.")
                return []
            
            if artist.name.lower() != artist_name.lower():
                self.logger.warning(f"⚠️ Búsqueda ambigua: Buscaste '{artist_name}' pero Jellyfin encontró '{artist.name}' (ID: {artist.artis_id})")

            tasks.append(EditTask(
                item_id=artist.artis_id, 
                name=artist.name, 
                type=ItemType.ARTIST
            ))

            if recursive:
                # Obtenemos álbumes usando la ruta probada de analyze.py
                albums = self.jf.get_items_by_artist(artist.artis_id)
                for album in albums:
                    tasks.append(EditTask(
                        item_id=album.id, 
                        name=album.name, 
                        type=ItemType.ALBUM,
                        parent_name=artist.name
                    ))
                    
                    # Bajamos al nivel de track para cada álbum
                    tracks = self.jf.get_tracks_by_album(album.id)
                    for track in tracks:
                        tasks.append(EditTask(
                            item_id=track.id, 
                            name=track.name, 
                            type=ItemType.TRACK,
                            parent_name=album.name
                        ))

        # Caso 2: Flujo desde Álbum individual
        elif album_id:
            # Para obtener el nombre del álbum necesitamos el raw_item
            raw_album = self.jf.get_raw_item(album_id)
            album_name = raw_album.get("Name", "Álbum Desconocido")
            
            tasks.append(EditTask(item_id=album_id, name=album_name, type=ItemType.ALBUM))
            
            if recursive:
                tracks = self.jf.get_tracks_by_album(album_id)
                for track in tracks:
                    tasks.append(EditTask(
                        item_id=track.id, 
                        name=track.name, 
                        type=ItemType.TRACK,
                        parent_name=album_name
                    ))

        # Caso 3: Track individual
        elif track_id:
            raw_track = self.jf.get_raw_item(track_id)
            tasks.append(EditTask(
                item_id=track_id, 
                name=raw_track.get("Name", "Track Desconocido"), 
                type=ItemType.TRACK
            ))

        return tasks

    def execute_tasks(
        self, 
        tasks: List[EditTask], 
        genres: List[str], 
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> List[EditResult]:
        """
        Recorre la lista de tareas y aplica la lista de géneros a cada ítem.
        
        Args:
            tasks: Lista de unidades de trabajo (EditTask).
            genres: Lista de géneros a añadir (e.g., ["Jazz", "Swing"]).
            progress_callback: Función opcional para actualizar la UI (barra de progreso).
        
        Returns:
            List[EditResult]: Lista de resultados de edición.
        """
        results: List[EditResult] = []

        for task in tasks:
            # Informar al callback para actualizar la descripción en la CLI
            if progress_callback:
                context = f" ({task.parent_name})" if task.parent_name else ""
                progress_callback(f"Procesando {task.type.value}: {task.name}{context}")

            # 1. Obtener metadata cruda (Una sola lectura por ítem)
            raw_data = self.jf.get_raw_item(task.item_id)
            if not raw_data:
                results.append(EditResult(
                    name=task.name, 
                    item_type=task.type, 
                    status=EditStatus.ERROR, 
                    message="No se pudo recuperar el ítem"
                ))
                continue

            current_genres = raw_data.get("Genres", [])
            original_count = len(current_genres)
            
            # 2. Añadir géneros faltantes (Lógica de conjunto)
            for g in genres:
                if g not in current_genres:
                    current_genres.append(g)

            # 3. Solo escribir si hubo cambios reales
            if len(current_genres) > original_count:
                raw_data["Genres"] = current_genres
                success = self.jf.update_item(task.item_id, raw_data)
                
                if success:
                    status = EditStatus.UPDATED
                    msg = f"Add: {', '.join([g for g in genres if g not in current_genres[:original_count]])}"
                else:
                    status = EditStatus.ERROR
                    msg = "Error al actualizar en el servidor"
            else:
                status = EditStatus.SKIPPED
                msg = "Ya contenía todos los géneros"

            results.append(EditResult(
                name=task.name, 
                item_type=task.type, 
                status=status, 
                message=msg
            ))

        return results