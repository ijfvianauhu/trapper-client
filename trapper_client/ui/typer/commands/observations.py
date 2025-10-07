import typer, logging,gettext
from trapper_client.TrapperClient import TrapperClient
from trapper_client.ui.typer.TyperUtils import TyperUtils

app = typer.Typer(help="Manage Observations")

logger = logging.getLogger(__name__)
_ = gettext.gettext

@app.command("classification-project",
    short_help=_("Retrieve all observations associated with a specific classification project."),
    help=_("This command fetches observations that belong to a classification project by its unique ID.")
)
def get_by_classification_project(
    ctx: typer.Context,
    cproject_id: str = typer.Argument(..., help=_("The unique ID of the classification project whose observations will be fetched")),
    export: str = typer.Option(None, help="Export results to CSV file")
) -> None:
    """
    Retrieve all observations associated with a specific classification project.

    This command fetches observations that belong to a classification project identified by its unique  ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        cproject_id(str): The unique ID of the classification project whose observations will be retrieved.

    Returns:
        None: Prints the list of media to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.observations.get_by_classification_project(cproject_id)

    if export:
        file = trapper_client.export_list_to_csv(result, output_file=export)
        TyperUtils.success(_(f"Observations stored successfully in {file}."))
    else:
        TyperUtils.json2Table(result, title=f"Observations obtained in classification project {cproject_id}", columns=["id","observationID","deploymentID","mediaID", "observationType", "scientificName", "bboxes"])
