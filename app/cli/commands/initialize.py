import sys
from rich.console import Console
from rich.table import Table
from app.settings.app_settings import Settings
from app.settings.env_content_file import write_content_to_file
from app.settings.env_file_path import get_env_paths

def initialize_config(
        console: Console, 
        settings: Settings, 
        host: str, 
        api_key: str, 
        app_name: str, 
        server_time_response: int,
        log_level:str = "INFO"
    ) -> None:
    """
    Crea los directorios y el archivo .env inicial.
    """
    # 1. Asegurar directorios base (logs, config, data)
    settings.ensure_dirs()

    # 2. Determinar ruta del .env de usuario
    env_paths = get_env_paths()
    user_env = env_paths[0] 

    if user_env.exists():
        console.print(f"[yellow]Advertencia:[/yellow] El archivo de configuración ya existe en: {user_env}")
        return
    
    # 3. Preparar contenido del archivo
    # Usamos el timezone por defecto de settings si no se pide por CLI
    content = write_content_to_file(
        app_name=app_name, 
        api_key=api_key, 
        host=host, 
        server_time_response=server_time_response,
        timezone=settings.TIMEZONE,
        log_level=log_level
    )

    # 4. Escritura física
    try:
        user_env.parent.mkdir(parents=True, exist_ok=True)
        user_env.write_text(content, encoding="utf-8")
        console.print("[bold green]✔[/bold green] Configuración inicial creada con éxito.")
    except Exception as e:
        console.print(f"[bold red]Error crítico al escribir la configuración:[/bold red] {e}")
        sys.exit(1)

    # 5. Feedback visual de lo creado
    table = Table(
        title="[bold magenta]Configuración Inicial Generada[/bold magenta]",
        show_header=True,
        border_style="blue",
    )
    table.add_column("Variable", style="cyan")
    table.add_column("Valor", style="green")
    
    table.add_row("Archivo", str(user_env))
    table.add_row("JELLIFYIN_HOST", host)
    table.add_row("API_KEY", f"{api_key[:4]}****{api_key[-4:]}") # Seguridad básica en el print
    table.add_row("APP_NAME", app_name)

    console.print(table)