import typer, logging,gettext
from trapper_client.TrapperClient import TrapperClient
from trapper_client.ui.typer.TyperUtils import TyperUtils

app = typer.Typer(help="Manage resources")

logger = logging.getLogger(__name__)
_ = gettext.gettext

@app.command("collection",
    short_help=_("Retrieve all resources associated with a specific collection"),
    help=_("This command fetches resources that belong to a collection indetified by its unique ID")
)
def get_by_collection(
    ctx: typer.Context,
    colllection_id: str = typer.Argument(..., help=_("The unique ID of the collection whose resources will be fetched"))
) -> None:
    """
    Retrieve all resources associated with a specific collection.

    This command fetches resources that belong to a collection identified by its unique project ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        colllection_id(str): The unique ID of the collection whose resources will be retrieved.

    Returns:
        None: Prints the list of resources to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.resources.get_by_collection(colllection_id)
    TyperUtils.json2Table(result, title=f"Resources used in collection {colllection_id}", columns=["pk","name","owner","url", "observation", "species"])

@app.command("location",
    short_help=_("Retrieve all resources associated with a specific location."),
    help=_("This command fetches resources that belong to a location identified by its unique ID.")
)
def get_by_research_project(
    ctx: typer.Context,
    location_id: str = typer.Argument(..., help=_("The unique ID of the location whose resources will be fetched"))
) -> None:
    """
    Retrieve all resources associated with a specific location.

    This command fetches resources that belong to a location identified by its unique ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        rproject_id(str): The unique ID of the location whose resources will be retrieved.

    Returns:
        None: Prints the list of collections to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.resources.get_by_location(location_id)
    TyperUtils.json2Table(result, title=f"Collections taken at location {location_id}", columns=["pk","name","deployment", "date_recorded", "detail_data"])

