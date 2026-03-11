
def write_content_to_file(app_name: str, api_key: str, host: str, timezone: str) -> str:
    default_env_content = f"""# GENRE EDITOR - AUTO-GENERATED CONFIG
APP_NAME={app_name}
API_KEY={api_key}
JELLIFYIN_HOST={host}
TIMEZONE={timezone}
"""
    return default_env_content