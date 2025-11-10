import typer, logging,gettext
from trapper_client.TrapperClient import TrapperClient
from trapper_client.ui.typer.TyperUtils import TyperUtils
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, BarColumn, ProgressColumn
from rich.text import Text
import time

app = typer.Typer(help="Manage Media")

logger = logging.getLogger(__name__)
_ = gettext.gettext

@app.command("classification-project",
    short_help=_("Retrieve all media associated with a specific classification project."),
    help=_("This command fetches media that belong to a classification project by its unique ID.")
)
def get_by_classification_project(
    ctx: typer.Context,
    cproject_id: str = typer.Argument(..., help=_("The unique ID of the classification project whose media will be fetched")),
    export: str = typer.Option(None, help="Export results to CSV file")
) -> None:
    """
    Retrieve all media associated with a specific classification project.

    This command fetches media that belong to a classification project identified by its unique  ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        cproject_id(str): The unique ID of the classification project whose media will be retrieved.

    Returns:
        None: Prints the list of media to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    columns_to_show=["id", "mediaID", "deploymentID",
                     # "captureMethod", "timestamp",
                     "filePath", "filePublic", "fileName",
                     #"fileMediatype", "exifData", "favorite", "mediaComments"
    ]

    result = trapper_client.media.get_by_classification_project(cproject_id)

    if export:
        trapper_client.export_list_to_csv(result, output_file=export)
        TyperUtils.success(_(f"Media stored successfully in {export}."))
    else:
        TyperUtils.json2Table(result, title=f"Media used in classification project {cproject_id}", columns=columns_to_show)

@app.command("classification-project",
    short_help=_("Retrieve all media associated with a specific classification project."),
    help=_("This command fetches media that belong to a classification project by its unique ID.")
)
def get_by_classification_project(
    ctx: typer.Context,
    cproject_id: str = typer.Argument(..., help=_("The unique ID of the classification project whose media will be fetched")),
    export: str = typer.Option(None, help="Export results to CSV file"),
    download: bool = typer.Option(False, help="Download medias")
) -> None:
    """
    Retrieve all media associated with a specific classification project.

    This command fetches media that belong to a classification project identified by its unique  ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        cproject_id(str): The unique ID of the classification project whose media will be retrieved.

    Returns:
        None: Prints the list of media to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]
    columns_to_show=["id", "mediaID", "deploymentID",
                     # "captureMethod", "timestamp",
                     "filePath", "filePublic", "fileName",
                     #"fileMediatype", "exifData", "favorite", "mediaComments"
    ]

    if download:
        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task(f"Downloading media from project {cproject_id}...", start=False)

            result = trapper_client.media.download_by_classification_project(
                cproject_id,
                zip_filename_base=f"media_cp_{cproject_id}"
            )

        TyperUtils.success(_(f"Media files stored successfully in {result}."))
    else:
        result = trapper_client.media.get_by_classification_project(cproject_id)

        if export:
            dir_name=trapper_client.export_list_to_csv(result, output_file=export)
            TyperUtils.success(_(f"Media stored successfully in {dir_name}."))
        else:
            TyperUtils.json2Table(result, title=f"Media used in classification project {cproject_id}", columns=columns_to_show)

@app.command("classification-project-only-animals",
    short_help=_("Retrieve media associated with a specific classification project which have all bb classified as animal."),
    help=_("This command fetches media, which have all bb classified as animal, that belong to a classification project by its unique ID."),
)
def get_by_classification_project_only_animals(
    ctx: typer.Context,
    cproject_id: str = typer.Argument(..., help=_("The unique ID of the classification project whose media will be fetched")),
    export: str = typer.Option(None, help="Export results to CSV file"),
    download: bool = typer.Option(False, help="Download medias")
) -> None:
    """
    Retrieve all media associated with a specific classification project.

    This command fetches media that belong to a classification project identified by its unique  ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        cproject_id(str): The unique ID of the classification project whose media will be retrieved.

    Returns:
        None: Prints the list of media to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    if download:
        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task(f"Downloading media from project {cproject_id}...", start=False)
            result = trapper_client.media.download_by_classification_project_only_animals(cproject_id, zip_filename_base=f"media_cp_only_animals_{cproject_id}")
            TyperUtils.success(_(f"Media files stored successfully in {result}."))
    else:
        result = trapper_client.media.get_by_classification_project_only_animals(cproject_id)

        if export:
            dir_name = trapper_client.export_list_to_csv(result, output_file=export)
            TyperUtils.success(_(f"Media stored successfully in {dir_name}."))
        else:
            TyperUtils.json2Table(result, title=f"Media used in classification project {cproject_id} labelled as animal", columns=["id","observationID","deploymentID","mediaID", "observationType", "scientificName"])

