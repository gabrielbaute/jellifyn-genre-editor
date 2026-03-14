import sys
from rich.console import Console
from argparse import ArgumentParser, Namespace

from app.services.jellyfin_client_service import JellyfinClientService
from app.settings.app_settings import settings
from app.settings.app_logs_settings import JGELogger

from app.cli.parser import create_parser
from app.cli.commands import (
    show_version, 
    initialize_config, 
    show_logs,
    show_config,
    analyze_artist,
    analyze_album, 
    analyze_track, 
    run_edit
)

JGELogger.setup_logging()

def main() -> None:
    parser: ArgumentParser = create_parser(settings=settings)
    args: Namespace = parser.parse_args()

    console = Console()

    if args.command == "version":
        show_version(console, settings)
    
    elif args.command == "init":
        initialize_config(
            console=console, 
            settings=settings, 
            host=args.host, 
            api_key=args.api_key, 
            app_name=args.app_name, 
            server_time_response=args.time_response
            
        )

    elif args.command == "config":
        show_config(console, settings)

    elif args.command == "analyze":
        jf_service = JellyfinClientService(settings)
        try:
            if not jf_service.verify_connection():
                return

            if args.track:
                analyze_track(console, jf_service, args.track)
            elif args.album:
                analyze_album(console, jf_service, args.album)
            elif args.artist:
                # Si solo pones artista, mostramos el artista
                analyze_artist(console, jf_service, args.artist)
                # Opcional: Podríamos llamar automáticamente a analyze_albums del artista aquí
            else:
                console.print("[yellow]Debes especificar --artist, --album o --track[/yellow]")
        finally:
            jf_service.close()

    elif args.command == "edit":
        jf_service = JellyfinClientService(settings)
        try:
            if not jf_service.verify_connection():
                return
            
            run_edit(console, jf_service, args)
        finally:
            jf_service.close()

    elif args.command == "logs":
        show_logs(console, settings, args.lines)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()