from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from app.services.jellyfin_client_service import JellyfinClientService

def analyze_artist(console: Console, jf_service: JellyfinClientService, artist_name: str) -> None:
    """
    Obtiene los datos de un artista y sus álbumes, presentándolos en formato tabular.
    """
    with console.status(f"[bold green]Consultando a Jellyfin por '{artist_name}'..."):
        try:
            artist = jf_service.get_artist_by_name(artist_name)
            # Recuperamos los álbumes del artista para el análisis completo
            albums = jf_service.get_items_by_artist(artist.artis_id)

        except Exception as e:
            console.print(f"[bold red]Error al obtener datos del artista:[/bold red] {e}")
            return
        
        except KeyboardInterrupt:
            console.print(f"\n[bold red]❌ Acción cancelada.[/bold red]")
            return


    # --- Tabla 1: Información General del Artista ---
    table = Table(
        title=f"Resultados de Análisis: [bold cyan]{artist.name}[/bold cyan]",
        header_style="bold magenta",
        border_style="bright_blue",
        show_lines=True
    )
    table.add_column("Propiedad", style="dim", width=15)
    table.add_column("Valor Detallado", style="white")

    table.add_row("ID de Artista", f"[yellow]{artist.artis_id}[/yellow]")
    table.add_row("Ruta en Disco", f"[blue]{artist.path}[/blue]")
    
    genres_str = ", ".join(artist.genres) if artist.genres else "[italic red]Sin géneros[/italic red]"
    table.add_row("Géneros", f"[green]{genres_str}[/green]")
    
    tags_str = ", ".join(artist.tags) if artist.tags else "[italic]Sin tags[/italic]"
    table.add_row("Tags", f"[magenta]{tags_str}[/magenta]")

    console.print(table)

    # --- Tabla 2: Listado de Álbumes (Crucial para IDs) ---
    if albums:
        album_table = Table(
            title=f"Discografía de {artist.name}",
            title_style="bold yellow",
            header_style="bold green",
            expand=True
        )
        album_table.add_column("Nombre del Álbum", style="cyan")
        album_table.add_column("ID de Álbum", style="dim", justify="center")
        album_table.add_column("Géneros", style="magenta")

        for album in albums:
            album_table.add_row(
                album.name,
                album.id,
                ", ".join(album.genres) if album.genres else "-"
            )
        
        console.print(album_table)
    else:
        console.print("[yellow]No se encontraron álbumes vinculados a este artista.[/yellow]")

    # --- Panel 3: GenreItems ---
    if artist.genre_items:
        gi_table = Table(box=None)
        gi_table.add_column("Nombre", style="cyan")
        gi_table.add_column("Genre ID", style="dim")
        for item in artist.genre_items:
            gi_table.add_row(item.name, item.genre_id)
        
        console.print(Panel(gi_table, border_style="dim", title="Metadatos de Sistema (GenreItems)"))

def analyze_album(console: Console, jf_service: JellyfinClientService, album_id: str) -> None:
    """Muestra los detalles de un álbum y lista sus tracks."""
    tracks = jf_service.get_tracks_by_album(album_id)
    
    table = Table(title=f"Tracks del Álbum ID: [bold yellow]{album_id}[/bold yellow]", border_style="green")
    table.add_column("Index", justify="right")
    table.add_column("Nombre", style="cyan")
    table.add_column("ID", style="dim")
    table.add_column("Géneros", style="magenta")

    for idx, track in enumerate(tracks, 1):
        table.add_row(
            str(idx),
            track.name,
            track.id,
            ", ".join(track.genres)
        )
    
    console.print(table)

def analyze_track(console: Console, jf_service: JellyfinClientService, track_id: str) -> None:
    """Muestra la metadata cruda y procesada de un track específico."""
    raw_item = jf_service.get_raw_item(track_id)
    
    table = Table(title=f"Detalle de Track: [bold]{raw_item.get('Name')}[/bold]", show_lines=True)
    table.add_column("Campo")
    table.add_column("Dato")

    table.add_row("ID", track_id)
    table.add_row("Ruta", raw_item.get("Path", "N/A"))
    table.add_row("Géneros (Genres)", str(raw_item.get("Genres", [])))
    table.add_row("GenreItems", str(raw_item.get("GenreItems", [])))
    
    console.print(table)