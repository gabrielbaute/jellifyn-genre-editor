
def write_content_to_file(
        app_name: str, 
        api_key: str, 
        host: str, 
        timezone: str, 
        server_time_response: int = 15,
        log_level: str = "INFO"
    ) -> str:
    """
    Escribe el contenido del archivo de configuración.

    Args:
        app_name (str): Nombre de la aplicación.
        api_key (str): Clave de API de Jellyfin.
        host (str): URL del servidor de Jellyfin.
        timezone (str): Zona horaria.
        server_time_response(int): Tiempo de respuesta del servidor.
        log_level (str): Nivel de registro.

    Returns:
        str: Contenido del archivo.
    """
    # Contenido del archivo
    default_env_content = f"""# GENRE EDITOR - AUTO-GENERATED CONFIG
APP_NAME={app_name}
API_KEY={api_key}
JELLIFYIN_HOST={host}
TIMEZONE={timezone}
SERVER_TIME_RESPONSE={server_time_response}
LOG_LEVEL={log_level}
"""
    return default_env_content