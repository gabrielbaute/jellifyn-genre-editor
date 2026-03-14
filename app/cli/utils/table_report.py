from typing import List
from rich.table import Table
from rich.console import Console

from app.enums import EditStatus
from app.schemas import EditResult

def display_edit_report(console: Console, results: List[EditResult]) -> None:
    """
    Genera una tabla resumen de la operación de edición.

    Args:
        console (Console): Objeto de consola de rich
        results (List[EditResult]): Lista de resultados de la operación de edición.
    
    Returns:
        None
    """
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
            EditStatus.REMOVED: "deep_pink1",
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
    removed = len([r for r in results if r.status == EditStatus.REMOVED])
    
    console.print(f"\n[bold]Resumen:[/bold] [green]{updated} actualizados[/green], "
                  f"[yellow]{skipped} omitidos[/yellow], [red]{errors} errores[/red]."
                  f" [deep_pink1]{removed} eliminados[/deep_pink1]")