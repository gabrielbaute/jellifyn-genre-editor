import httpx
import logging
from typing import Any, Dict, List

from app.schemas import Album, Artist, Track
from app.settings.app_settings import Settings
from app.services.jellyfin_parser import JellyfinParser
from app.errors import TimeOutError, AuthError, ApiError, GenreEditorError, ConnectionError

class JellyfinClientService:
    """
    Cliente para la interacción inicial con la API de Jellyfin.
    
    Se centra en la validación de credenciales y la exploración de endpoints
    antes de definir modelos de datos estrictos.
    """

    def __init__(self, settings: Settings):
        """
        Inicializa el cliente.
        
        Args:
            settings (Settings): Configuraciones de la aplicación.
        """
        logging.getLogger("httpx").setLevel(logging.WARNING)
        self.host: str = settings.JELLIFYIN_HOST.rstrip("/")
        self.api_key: str = settings.API_KEY
        self.app_name: str = settings.APP_NAME
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parser = JellyfinParser()
        
        # Jellyfin prefiere este formato de cabecera para identificar la app
        self.headers: Dict[str, str] = {
            "X-Emby-Authorization": (
                f'MediaBrowser Client="{self.app_name}", '
                f'Device="PythonScript", '
                f'DeviceId="CLI-Tool", '
                f'Version="0.1.0", '
                f'Token="{self.api_key}"'
            ),
            "Accept": "application/json"
        }
        
        self._client: httpx.Client = httpx.Client(
            base_url=self.host, 
            headers=self.headers,
            timeout=float(settings.SERVER_TIME_RESPONSE)
        )

    def _handle_httpx_error(self, e: Exception, context: str):
        """Mapea errores de httpx a tus excepciones personalizadas."""
        # Si ya es una de nuestras excepciones, la dejamos pasar
        if isinstance(e, (AuthError, ApiError, TimeOutError, GenreEditorError)):
            raise e
        
        if isinstance(e, httpx.TimeoutException):
            raise TimeOutError(f"Tiempo de espera agotado en {context}", details={"url": str(e.request.url)})
        
        if isinstance(e, (httpx.ConnectError, httpx.RequestError)):
            raise ConnectionError(f"Error de conexión en {context}", details={"url": str(e.request.url)})
        
        if isinstance(e, httpx.HTTPStatusError):
            code = e.response.status_code
            if code in (401, 403):
                raise AuthError(f"Error de autenticación en Jellyfin. Revisa tu API Key.", details={"status": code})
            if code == 404:
                raise ApiError(f"Recurso no encontrado: {context}", details={"status": 404})
            if code == 400:
                raise ApiError(f"Solicitud incorrecta: {context}", details={"status": 400})
            if code == 500:
                raise ApiError(f"Error interno del servidor: {context}", details={"status": 500})
            if code == 503:
                raise ApiError(f"Servicio no disponible: {context}", details={"status": 503})
            
            raise ApiError(f"Error de API ({code}) en {context}", details={"response": e.response.text})

        raise GenreEditorError(f"Error inesperado en {context}: {str(e)}")

    def _raw_get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Método auxiliar para 'explorar' la API. 
        Retorna el JSON crudo para que podamos analizarlo y luego crear los modelos.
        """
        try:
            response = self._client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._handle_httpx_error(e, endpoint)

    def _raw_post(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """
        Envía una petición POST al servidor.
        
        Args:
            endpoint (str): El endpoint de la API.
            data (Dict[str, Any]): El cuerpo de la petición.
            
        Returns:
            bool: True si la actualización fue exitosa (Status 204).
        """
        try:
            response = self._client.post(endpoint, json=data)
            response.raise_for_status()
            # El status 204 No Content es el éxito estándar en Jellyfin para updates
            return response.status_code == 204
        except Exception as e:
            self._handle_httpx_error(e, endpoint)

    def get_current_user_id(self) -> str:
        """Obtiene el ID del primer usuario administrador disponible."""
        # El endpoint /Users devuelve la lista de usuarios
        response = self._client.get("/Users")
        response.raise_for_status()
        users = response.json()
        # Retornamos el ID del primer usuario (típicamente el admin)
        return users[0]["Id"]

    def verify_connection(self) -> bool:
        """
        Verifica si la API Key es válida y el servidor está accesible.
        Utiliza el endpoint /System/Info que es público pero requiere auth mínima.
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario.
        """
        try:
            # Intentamos obtener información del sistema para validar el Token
            response = self._client.get("/System/Info")
            response.raise_for_status()
            self.logger.info(f"[OK] Conexión establecida con: {response.json().get('ServerName')}")
            return True
        except Exception as e:
            self._handle_httpx_error(e, "verify_connection")
            return False

    def close(self) -> None:
        """Cierra la sesión del cliente httpx."""
        self._client.close()

    def update_item_metadata(self, item_id: str, updated_data: Dict[str, Any]) -> bool:
        """
        Actualiza los metadatos de un ítem.
        """
        endpoint = f"/Items/{item_id}"
        self.logger.info(f"Actualizando metadatos para el ítem: {item_id}")
        return self._raw_post(endpoint, updated_data)

    def get_artist_by_name(self, name: str) -> Artist:
        """
        Obtiene el objeto crudo de un artista por su nombre exacto.

        Args:
            name (str): El nombre exacto del artista.
        
        Returns:
            Artist: Un objeto Artist
        """
        endpoint = f"/Artists/{name}"
        self.logger.info(f"Obteniendo artista: {name}")
        data = self._raw_get(endpoint)
        return self.parser.parse_artist(data)

    def get_items_by_artist(self, artist_id: str, item_type: str = "MusicAlbum") -> List[Album]:
        """
        Busca ítems (Albums o Audio) vinculados a un ArtistId.
        
        Args:
            artist_id (str): El ID del artista.
            item_type (str): Tipo de item (MusicAlbum)
        
        Returns:
            List[Album]: Una lista de objetos Album.
        """
        params = {
            "ArtistIds": artist_id,
            "IncludeItemTypes": item_type,
            "Recursive": "true",
            "Fields": "Genres,Tags,Path"
        }
        self.logger.info(f"Realizando búsqueda de Albums a partir de ID de artista: {artist_id}")
        data = self._raw_get("/Items", params=params)
        albums = [self.parser.parse_album(item) for item in data["Items"]]
        return albums

    def get_tracks_by_album(self, album_id: str) -> List[Track]:
        """
        Obtiene los tracks (items de tipo Audio) contenidos en un álbum.
        
        Args:
            album_id (str): El ID del álbum (MusicAlbum).
            
        Returns:
            List[Track]: Una lista de objetos Track.
        """
        params = {
            "parentId": album_id,
            "IncludeItemTypes": "Audio",
            "Recursive": "true",
            "Fields": "Genres,Tags,Path,GenreItems"
        }
        self.logger.info(f"Obteniendo tracks para el álbum ID: {album_id}")
        data = self._raw_get("/Items", params=params)
        tracks = [self.parser.parse_track(item) for item in data["Items"]]
        return tracks

    def get_raw_item(self, item_id: str) -> Dict[str, Any]:
        """Obtiene la metadata completa y cruda de un ítem por su ID."""
        user_id = self.get_current_user_id() 
        params = {"userId": user_id}
        return self._raw_get(f"/Items/{item_id}", params=params)

    def update_item(self, item_id: str, data: Dict[str, Any]) -> bool:
        """Envía el objeto completo de vuelta para actualizar el ítem."""
        # Es fundamental asegurarse de que el servidor no sobrescriba 
        # nuestros cambios en el próximo escaneo.
        data["LockData"] = True 
        return self._raw_post(f"/Items/{item_id}", data)