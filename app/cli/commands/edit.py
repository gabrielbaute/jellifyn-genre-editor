from typing import List
from rich.table import Table
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from app.enums import EditStatus, ItemType
from app.schemas import EditResult, EditTask
from app.errors import GenreEditorError, ApiError
from app.services.genre_editor_cli import GenreEditorCLI 
from app.services.jellyfin_client_service import JellyfinClientService

def run_edit(console: Console, jf_service: JellyfinClientService, args) -> None:
    """
    Punto de entrada principal para el comando 'edit'.
    Implementa el patrón Recolección -> Ejecución -> Reporte.
    """
    cli_editor = GenreEditorCLI(jf_service)
    
    # Normalización de géneros (soporta tanto ';' como ',' como separadores)
    genres = [g.strip() for g in args.genre.replace(';', ',').split(',') if g.strip()]
    
    if not genres:
        console.print("[bold red]Error:[/bold red] Debes especificar al menos un género válido.")
        return

    try:
        # FASE 1: Recolección (Building the Task Map)
        with console.status("[bold green]Analizando jerarquía en Jellyfin y recolectando tareas..."):
            tasks: List[EditTask] = cli_editor.build_task_list(
                artist_name=args.artist,
                album_id=args.album,
                track_id=args.track,
                recursive=args.recursive
            )

        if not tasks:
            console.print("[yellow]No se encontraron ítems para procesar con los criterios proporcionados.[/yellow]")
            return

        # FASE 2: Ejecución con Progreso Visual
        all_results: List[EditResult] = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None, pulse_style="yellow"),
            TaskProgressColumn(),
            console=console,
            transient=True  # Limpia la barra al terminar para mostrar solo el reporte
        ) as progress:
            
            # El total de pasos es el número de ítems (ya que procesamos todos los géneros por ítem)
            edit_task_id = progress.add_task("Iniciando edición...", total=len(tasks))
            
            # Definimos el callback para que haga AMBAS cosas
            def update_ui(msg: str):
                # 1. Actualiza el texto descriptivo
                progress.update(edit_task_id, description=msg)
                # 2. Incrementa el contador de la barra en 1
                progress.advance(edit_task_id, advance=1)

            # Ejecución centralizada
            all_results = cli_editor.execute_tasks(
                tasks=tasks,
                genres=genres,
                progress_callback=update_ui
            )
            
            # Al terminar cada ítem, avanzamos la barra
            for _ in tasks:
                progress.advance(edit_task_id)

        # FASE 3: Reporte Final
        display_edit_report(console, all_results)

    except ApiError as e:
        console.print(f"\n[bold red]❌ Error de API:[/bold red] {e.message}")
    except Exception as e:
        console.print(f"\n[bold red]💥 Error crítico inesperado:[/bold red] {str(e)}")

def display_edit_report(console: Console, results: List[EditResult]) -> None:
    """Genera una tabla resumen de la operación de edición."""
    # (Mantenemos tu implementación de display_edit_report tal cual la proporcionaste)
    if not results:
        return

    table = Table(
        title="\n[bold]REPORTE DE EDICIÓN[/bold]",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
        expand=True
    )
    
    table.add_column("Ítem", style="cyan", no_wrap=True)
    table.add_column("Tipo", style="dim", justify="center")
    table.add_column("Estado", justify="center")
    table.add_column("Detalle", style="italic")

    for res in results:
        status_color = {
            EditStatus.UPDATED: "green",
            EditStatus.SKIPPED: "yellow",
            EditStatus.ERROR: "red"
        }.get(res.status, "white")
        
        table.add_row(
            res.name,
            res.item_type.value,
            f"[{status_color}]{res.status}[/{status_color}]",
            res.message or "-"
        )

    console.print(table)
    
    updated = len([r for r in results if r.status == EditStatus.UPDATED])
    skipped = len([r for r in results if r.status == EditStatus.SKIPPED])
    errors = len([r for r in results if r.status == EditStatus.ERROR])
    
    console.print(f"\n[bold]Resumen:[/bold] [green]{updated} actualizados[/green], "
                  f"[yellow]{skipped} omitidos[/yellow], [red]{errors} errores[/red].")