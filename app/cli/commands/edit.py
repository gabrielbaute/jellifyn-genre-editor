from typing import List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from app.enums import EditStatus
from app.errors import ApiError
from app.schemas import EditResult
from app.services.genre_editor_cli import GenreEditorCLI 
from app.services.jellyfin_client_service import JellyfinClientService
from app.cli.utils.table_report import display_edit_report

def run_edit(console: Console, jf_service: JellyfinClientService, args) -> None:
    """
    Punto de entrada para 'edit'. Ahora con soporte para --preview y 
    lógica de progreso simplificada.
    """
    cli_editor = GenreEditorCLI(jf_service)
    genres_to_add = [g.strip() for g in args.genre.replace(';', ',').split(',') if g.strip()]
    
    if not genres_to_add:
        console.print("[bold red]Error:[/bold red] Debes especificar al menos un género.")
        return

    if args.preview:
        console.print("[bold yellow] MODO PREVIEW: Simulando adición de géneros.[/bold yellow]\n")

    try:
        # FASE 1: Recolección
        with console.status("[bold green]Analizando jerarquía..."):
            tasks = cli_editor.build_task_list(
                artist_name=args.artist,
                album_id=args.album,
                track_id=args.track,
                recursive=args.recursive
            )

        if not tasks:
            console.print("[yellow]No se encontraron ítems.[/yellow]")
            return

        all_results: List[EditResult] = []

        # FASE 2: Ejecución/Simulación (Bucle limpio estilo 'remove')
        with Progress(
            SpinnerColumn(),
            BarColumn(pulse_style="yellow"),
            TaskProgressColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            
            task_id = progress.add_task("Editando...", total=len(tasks))

            for task in tasks:
                # Actualizamos descripción (limitando a 45 chars como en remove)
                progress.update(task_id, description=f"Procesando: {task.name[0:45]}")
                
                # Obtenemos data cruda
                raw_data = jf_service.get_raw_item(task.item_id)
                current_genres = raw_data.get("Genres", [])
                
                # Identificamos qué géneros de la lista NO están ya presentes
                to_add = [g for g in genres_to_add if g not in current_genres]

                if to_add:
                    if args.preview:
                        status = EditStatus.UPDATED
                        msg = f"[PREVIEW] Se añadiría: {', '.join(to_add)}"
                    else:
                        # EJECUCIÓN REAL
                        raw_data["Genres"] = current_genres + to_add
                        success = jf_service.update_item(task.item_id, raw_data)
                        status = EditStatus.UPDATED if success else EditStatus.ERROR
                        msg = f"Añadidos: {', '.join(to_add)}" if success else "Error API"
                else:
                    status = EditStatus.SKIPPED
                    msg = "Ya contiene todos los géneros especificados"

                all_results.append(EditResult(name=task.name, item_type=task.type, status=status, message=msg))
                progress.advance(task_id)

        # FASE 3: Reporte
        display_edit_report(console, all_results)

    except ApiError as e:
        console.print(f"\n[bold red]❌ Error de API:[/bold red] {e.message}")
    except Exception as e:
        console.print(f"\n[bold red]💥 Error crítico:[/bold red] {str(e)}")
    except KeyboardInterrupt:
        console.print(f"\n[bold red]❌ Acción cancelada por el usuario.[/bold red]")