from typing import List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from app.enums import EditStatus
from app.schemas import EditResult
from app.errors.api_error import ApiError
from app.services.genre_editor_cli import GenreEditorCLI, EditTask
from app.services.jellyfin_client_service import JellyfinClientService
from app.cli.utils.table_report import display_edit_report

def run_remove(console: Console, jf_service: JellyfinClientService, args) -> None:
    cli_editor = GenreEditorCLI(jf_service)
    genres_to_remove = [g.strip() for g in args.genre.replace(';', ',').split(',') if g.strip()]
    
    if args.preview:
        console.print("[bold yellow] MODO PREVIEW: No se realizarán cambios reales en Jellyfin.[/bold yellow]\n")

    try:
        # FASE 1: Recolección
        with console.status("[bold blue]Buscando ítems para limpieza..."):
            tasks = cli_editor.build_task_list(
                artist_name=args.artist,
                album_id=args.album,
                track_id=args.track,
                recursive=args.recursive
            )

        if not tasks:
            console.print("[yellow]No se encontraron ítems que coincidan.[/yellow]")
            return

        all_results: List[EditResult] = []

        # FASE 2: Simulación o Ejecución
        with Progress(
            SpinnerColumn(), 
            BarColumn(), 
            TaskProgressColumn(), 
            TextColumn("[bold red]{task.description}"), 
            console=console, 
            transient=True
        ) as progress:
            
            remove_task_id = progress.add_task("Procesando...", total=len(tasks))

            for task in tasks:
                progress.update(remove_task_id, description=f"Evaluando: {task.name[0:45]}")
                
                raw_data = jf_service.get_raw_item(task.item_id)
                current_genres = raw_data.get("Genres", [])
                
                found = [g for g in current_genres if g in genres_to_remove]
                
                if found:
                    if args.preview:
                        status = EditStatus.REMOVED # Marcamos como "sería actualizado"
                        msg = f"[PREVIEW]{', '.join(found)}"
                    else:
                        # EJECUCIÓN REAL
                        new_genres = [g for g in current_genres if g not in genres_to_remove]
                        raw_data["Genres"] = new_genres
                        success = jf_service.update_item(task.item_id, raw_data)
                        status = EditStatus.REMOVED if success else EditStatus.ERROR
                        msg = f"Eliminados: {', '.join(found)}" if success else "Error API"
                else:
                    status = EditStatus.SKIPPED
                    msg = "No contiene los géneros especificados"

                all_results.append(EditResult(name=task.name, item_type=task.type, status=status, message=msg))
                progress.advance(remove_task_id)

        # FASE 3: Reporte
        display_edit_report(console, all_results)
        
        if args.preview:
            console.print("\n[bold yellow]Fin del Preview. Revisa la tabla superior para ver los cambios planeados.[/bold yellow]")

    except ApiError as e:
        console.print(f"\n[bold red]❌ Error de API:[/bold red] {e.message}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    except KeyboardInterrupt:
        console.print(f"\n[bold red]❌ Acción cancelada.[/bold red]")