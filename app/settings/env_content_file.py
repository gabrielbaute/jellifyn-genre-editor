
def write_content_to_file(app_name: str, api_key: str, host: str, timezone: str, server_time_response: int = 15) -> str:
    default_env_content = f"""# GENRE EDITOR - AUTO-GENERATED CONFIG
APP_NAME={app_name}
API_KEY={api_key}
JELLIFYIN_HOST={host}
TIMEZONE={timezone}
SERVER_TIME_RESPONSE={server_time_response}
"""
    return default_env_content