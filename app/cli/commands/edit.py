from typing import List

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from app.errors import ApiError
from app.schemas import EditResult, EditTask
from app.services.genre_editor_cli import GenreEditorCLI 
from app.services.jellyfin_client_service import JellyfinClientService
from app.cli.utils.table_report import display_edit_report

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
