from typing import List
from rich.table import Table
from rich.console import Console

from app.schemas import EditResult
from app.enums import EditStatus, ItemType
from app.services.genre_editor import GenreEditor
from app.services.jellyfin_client_service import JellyfinClientService

def display_edit_report(console: Console, results: List[EditResult]) -> None:
    """Genera una tabla resumen de la operación de edición."""
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
        # Mapeo de colores según el Enum EditStatus
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
    
    # Resumen cuantitativo
    updated = len([r for r in results if r.status == EditStatus.UPDATED])
    skipped = len([r for r in results if r.status == EditStatus.SKIPPED])
    errors = len([r for r in results if r.status == EditStatus.ERROR])
    
    console.print(f"\n[bold]Resumen:[/bold] [green]{updated} actualizados[/green], "
                  f"[yellow]{skipped} omitidos[/yellow], [red]{errors} errores[/red].")

def run_edit(console: Console, jf_service: JellyfinClientService, args) -> None:
    """
    Ejecuta la edición de géneros y muestra el reporte final.
    """
    editor = GenreEditor(jf_service)
    genre = args.genre
    all_results: List[EditResult] = []

    with console.status(f"[bold green]Procesando cambios para: {genre}..."):
        # Caso 1: Artista
        if args.artist:
            # Primero el ítem del artista (atómico, devolvemos EditResult manual)
            artist_data = jf_service.get_artist_by_name(args.artist)
            if artist_data:
                status = editor._add_genre_to_an_artist_item(artist_data.artis_id, genre)
                all_results.append(EditResult(name=artist_data.name, item_type=ItemType.ARTIST, status=status))
                
                if args.recursive:
                    all_results.extend(editor.add_genre_to_all_artist_tracks(args.artist, genre))
            else:
                console.print(f"[red]Error: Artista '{args.artist}' no encontrado.[/red]")
                return

        # Caso 2: Álbum
        elif args.album:
            # Editamos el álbum
            all_results.append(editor.add_genre_to_album(args.album, genre))
            
            # Si es recursivo, editamos sus tracks
            if args.recursive:
                all_results.extend(editor.add_genre_to_album_tracks(args.album, genre))

        # Caso 3: Track individual
        elif args.track:
            status = editor._add_genre_to_single_track(args.track, genre)
            # Como el método atómico no sabe el nombre sin otra petición, 
            # podrías pasar el ID como nombre o mejorar el atómico para que devuelva el nombre.
            all_results.append(EditResult(name=f"Track ID: {args.track}", item_type=ItemType.TRACK, status=status))
        
        else:
            console.print("[yellow]Debes especificar un objetivo: --artist, --album o --track[/yellow]")
            return

    # Al finalizar el 'status' (spinner), pintamos la tabla
    display_edit_report(console, all_results)