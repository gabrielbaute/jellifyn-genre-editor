"""
Version command for the CLI.
"""
from rich.console import Console
from rich.table import Table

from app.settings.app_settings import Settings

def show_version(console: Console, settings: Settings) -> None:
    """
    Muestra la versión de la CLI.

    Args:
        console (Console): Objeto Console.

    Returns:
        None
    """
    console = Console()
    table = Table(
        title=f"[bold magenta]{settings.APP_NAME}[/bold magenta]",
        show_header=False,
        border_style="blue",
        padding=(0, 2),
    )
    table.add_column("Key", style="cyan", justify="right")
    table.add_column("Value", style="green")
    
    table.add_row("[yellow]Build[/yellow]", "[bold]stable[/bold]")
    table.add_row("Versión", f"[bold]{settings.APP_VERSION}[/bold]")
    table.add_row("Author", "Gabriel Baute")
    table.add_row("License", "MIT")
    table.add_row("Repo", "https://github.com/gabrielbaute/jellifyn-genre-editor")

    console.print(table)