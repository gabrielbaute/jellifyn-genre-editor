from pathlib import Path
from argparse import ArgumentParser

from app.settings.app_settings import Settings


def create_parser(settings: Settings) -> ArgumentParser:
    """
    Parser de comandos de entrada.

    Returns:
        ArgumentParser: Objeto ArgumentParser.
    """
    parser = ArgumentParser(
        prog=f"{settings.APP_NAME}",
        usage="genre-editor [options]",
        description="Edita las etiquetas de género en los tracks e items de Jellyfin.",
        add_help=True,
        allow_abbrev=True,
        exit_on_error=True
        )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands available")
    
    # -------------------------------------------
    # Subcommand: version
    # -------------------------------------------
    subparsers.add_parser("version", help="Shows CLI version")

    # -------------------------------------------
    # Subcommand: init
    # -------------------------------------------
    init_parser = subparsers.add_parser("init", help="Initialize configuration and directories")
    init_parser.add_argument("--host", type=str, required=True, help="Jellyfin server URL (e.g. http://192.168.1.10:8096)")
    init_parser.add_argument("--api-key", type=str, required=True, help="Your Jellyfin API Key")
    init_parser.add_argument("--time-response", type=int, default=15, help="Server time response for connect validation.")
    init_parser.add_argument("--app-name", type=str, default="GenreEditor", help="Custom name for this client")

    # -------------------------------------------
    # Subcommand: analyze
    # -------------------------------------------
    analyze_parser = subparsers.add_parser("analyze", help="Analiza los metadatos de un artista o álbum")
    analyze_parser.add_argument("--artist", type=str, required=True, help="Nombre del artista a analizar")
    analyze_parser.add_argument("--album", type=str, help="ID del álbum")
    analyze_parser.add_argument("--track", type=str, help="ID del track")

    # -------------------------------------------
    # Subcommand: edit
    # -------------------------------------------
    edit_parser = subparsers.add_parser("edit", help="Edita géneros de artistas, álbumes o tracks.")
    edit_parser.add_argument("--genre", type=str, required=True, help="Género que se desea añadir.")
    
    # Flags de objetivo
    edit_parser.add_argument("--artist", type=str, help="Nombre del artista.")
    edit_parser.add_argument("--album", type=str, help="ID del álbum.")
    edit_parser.add_argument("--track", type=str, help="ID del track.")
    
    # Flag opcional para procesar en cascada
    edit_parser.add_argument("--recursive", action="store_true", help="Si se usa con --artist o --album, aplica el género también a todos los tracks.")

    return parser