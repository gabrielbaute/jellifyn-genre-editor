from app.settings.app_settings import settings
from app.settings.app_logs_settings import JGELogger
from app.services.genre_editor import GenreEditor
from app.services.jellyfin_client_service import JellyfinClientService

JGELogger.setup_logging()

def main():
    # Inicializamos el servicio base
    jf_service = JellyfinClientService(settings)
    
    # Inicializamos el editor de géneros
    editor = GenreEditor(jf_service)

    try:
        # Escenario A: Editar todo un artista
        print("--- Editando Artista: Indila ---")
        editor.add_genre_to_all_artist_tracks("Em Beihold", "Alternative Pop")

        # Escenario B: Editar un álbum específico
        # Si ya conoces el ID o lo obtienes de una búsqueda
        # editor.add_genre_to_album_tracks("id_del_album", "Synthpop")

    finally:
        jf_service.close()

if __name__ == "__main__":
    main()