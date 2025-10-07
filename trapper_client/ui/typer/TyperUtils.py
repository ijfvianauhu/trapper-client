from pathlib import Path

from rich.console import Console
import logging
import typer
from typing import Optional, List, Union
from pydantic import BaseModel
from rich.table import Table
from rich.panel import Panel

class TyperUtils:
    console = Console()
    logger = logging.getLogger(__name__)

    @staticmethod
    def info(message: str):
        TyperUtils.console.print(f"[blue]:information:[/blue] {message}")
        TyperUtils.logger.info(message)

    @staticmethod
    def warning(message: str):
        TyperUtils.console.print(f"[orange]:warning:[/orange] {message}")
        TyperUtils.logger.warning(message)

    @staticmethod
    def error(message: str):
        TyperUtils.console.print(f"[red]:cross_mark:[/red] {message}")
        TyperUtils.logger.error(message)

    @staticmethod
    def fatal(message: str):
        TyperUtils.console.print(f"[red]:skull:[/red] {message}")
        TyperUtils.logger.critical(message)
        raise typer.Exit(code=1)

    @staticmethod
    def success(message: str):
        TyperUtils.console.print(f"[green]:white_check_mark:[/green] {message}")
        TyperUtils.logger.info(message)

    @staticmethod
    def validate_yaml_file(path: Path):
        import yaml
        try:
            with open(path, 'r') as file:
                yaml.safe_load(file)
            return True
        except yaml.YAMLError as e:
            raise ValueError((f"YAML file '{str(Path)}' is invalid: {e}"))
        except FileNotFoundError:
            raise ValueError((f"YAML file '{str(Path)}' not found."))

    @staticmethod
    def validate_zip_file(path: Path):
        import zipfile
        try:
            with zipfile.ZipFile(path, 'r') as zip_ref:
                bad_file = zip_ref.testzip()
                if bad_file is not None:
                    raise ValueError(f"ZIP file '{Path}' is corrupted at file '{bad_file}'.")

        except zipfile.BadZipFile:
            raise ValueError(f"ZIP file '{Path}' is not a zip file or it is corrupted.")
        except FileNotFoundError:
            raise ValueError(f"ZIP file '{Path}' not found.")

    @staticmethod
    def json2Table(
            data: Union[BaseModel, List[dict]],
            columns: Optional[List[str]] = None,
            title: str = "Table"
    ):
        """
        Convert a Pydantic BaseModel or a list of dicts to a Rich table and print it.

        Parameters
        ----------
        data : BaseModel | list[dict]
            Pydantic model containing 'results' or a plain list of dictionaries.
        columns : list[str], optional
            List of columns to display. Defaults to all keys of the first row.
        title : str, optional
            Table title. Defaults to "Table".
        """
        # Extraer filas
        if isinstance(data, BaseModel):
            rows = [item.model_dump() for item in getattr(data, "results", [data])]
        elif isinstance(data, list):
            rows = data
        else:
            raise ValueError("Data must be a Pydantic BaseModel or a list of dicts")

        if not rows:
            TyperUtils.console.print("No data to display")
            return

        # Determinar columnas
        if columns is None:
            columns = list(rows[0].keys())

        # Crear tabla
        table = Table(title=title)
        for col in columns:
            table.add_column(col, justify="left")

        # Añadir filas
        for row in rows:
            table.add_row(*[str(row.get(col, "")) for col in columns])

        TyperUtils.console.print(table)

        # Mostrar los campos disponibles
        available_fields = list(rows[0].keys())
        TyperUtils.console.print(
            f"[dim]Available fields:[/dim] [cyan]{', '.join(available_fields)}[/cyan]"
        )

    @staticmethod
    def print_pydantic_card(obj: BaseModel, title: str = "Pydantic Object") -> None:
        """
        Print a Pydantic object as a formatted card using Rich.

        Args:
            obj (BaseModel): The Pydantic object to display.
            title (str, optional): The title of the card. Defaults to "Pydantic Object".
        """
        table = Table(show_header=False, box=None)
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="white")

        # Pydantic v2 usa model_dump, v1 usa dict()
        data = obj.model_dump() if hasattr(obj, "model_dump") else obj.dict()

        for field, value in data.items():
            if isinstance(value, list):
                if value:  # lista no vacía
                    formatted = "\n".join([f"- {item}" for item in value])
                else:
                    formatted = "[dim]empty list[/dim]"
                table.add_row(field, formatted)
            else:
                table.add_row(field, str(value))

        TyperUtils.console.print(Panel(table, title=title, expand=False))