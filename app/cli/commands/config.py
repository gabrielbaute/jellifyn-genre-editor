from rich.console import Console
from rich.table import Table
from app.settings.app_settings import Settings

def show_config(console: Console, settings: Settings) -> None:
    """
    Muestra las variables de entorno actuales cargadas desde el .env.
    """
    table = Table(
        title="\n[bold]CONFIGURACIÓN ACTUAL DE JGE[/bold]",
        show_header=True,
        header_style="bold cyan",
        border_style="bright_blue",
        expand=True
    )

    table.add_column("Variable", style="magenta", no_wrap=True)
    table.add_column("Valor Actual", style="green")
    table.add_column("Origen/Estado", style="dim", justify="center")

    # Mapeamos las variables del objeto settings
    config_data = [
        ("Nombre de App", settings.APP_NAME, "Settings"),
        ("Host Jellyfin", settings.JELLIFYIN_HOST, "Settings"),
        ("API Key", settings.API_KEY, "Secret"),
        ("Nivel de Log", settings.LOG_LEVEL if hasattr(settings, 'LOG_LEVEL') else "INFO", "Env"),
        ("Ruta Config", str(settings.CONFIG_PATH), "System"),
        ("Ruta Logs", str(settings.LOGS_PATH if hasattr(settings, 'LOGS_PATH') else settings.BASE_PATH / "logs"), "System"),
    ]

    for var, value, source in config_data:
        table.add_row(var, str(value), source)

    console.print(table)
    
    # Nota sobre el archivo físico
    if settings.CONFIG_PATH.exists():
        console.print(f"\n[dim]Archivo de configuración cargado desde: {settings.CONFIG_PATH}[/dim]")
    else:
        console.print("\n[bold yellow]Aviso:[/bold yellow] No se detectó archivo .env físico, usando valores por defecto.")