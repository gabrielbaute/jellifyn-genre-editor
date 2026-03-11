import sys
import secrets
import logging
from app.settings.env_file_path import get_env_paths

logger = logging.getLogger("Bootstrap")


def bootstrap_config() -> None:
    """
    Prepara el entorno, directorios y variables mínimas para el primer arranque.
    """
    # Usamos la primera ruta de la tupla (la del usuario) para el bootstrap
    env_paths = get_env_paths()
    user_env = env_paths[0] 
    
    # Si el archivo ya existe, no hacemos nada, dejamos que Pydantic cargue
    if user_env.exists():
        return

    print(f"--- PRIMER ARRANQUE: Configurando entorno en {user_env.parent} ---")

    # 1. Crear directorios (Config, Data, etc.)
    user_env.parent.mkdir(parents=True, exist_ok=True)

    # 3. Contenido inicial del .env
    # Nota: Aquí puedes poner los valores por defecto que el usuario podría querer cambiar
    default_env_content = f"""# GENRE EDITOR - AUTO-GENERATED CONFIG
APP_NAME=GenreEditor
API_KEY=
"""
    try:
        user_env.write_text(default_env_content, encoding="utf-8")
        logger.info("--- Configuración inicial creada con éxito ---")
    except Exception as e:
        print(f"Error crítico al escribir la configuración: {e}")
        sys.exit(1)