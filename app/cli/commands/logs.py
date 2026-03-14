import os
from pathlib import Path
from collections import deque
from rich.console import Console
from rich.panel import Panel
from app.settings.app_settings import Settings

def show_logs(console: Console, settings: Settings, lines: int) -> None:
    """
    Lee y muestra las últimas N líneas del archivo de log.
    """
    log_file: Path = settings.LOGS_PATH / f"{settings.APP_NAME}.log"

    if not log_file.exists():
        console.print(f"[bold red]Error:[/bold red] El archivo de log no existe en {log_file}")
        return

    try:
        # Usamos deque con maxlen para mantener solo las últimas N líneas en memoria
        with open(log_file, "r", encoding="utf-8") as f:
            last_lines = deque(f, maxlen=lines)

        content = "".join(last_lines)
        
        # Presentación elegante con Rich
        console.print(Panel(
            content.strip(),
            title=f"Últimas {lines} líneas de: {log_file.name}",
            subtitle=f"Ruta: {log_file}",
            border_style="dim",
            padding=(1, 1)
        ))

    except Exception as e:
        console.print(f"[bold red]Error al leer el archivo de log:[/bold red] {str(e)}")