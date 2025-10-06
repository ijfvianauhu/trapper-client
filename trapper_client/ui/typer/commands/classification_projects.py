import typer, logging,gettext
from trapper_client.TrapperClient import TrapperClient
from trapper_client.ui.typer.TyperUtils import TyperUtils

app = typer.Typer(help="Manage Classification Projects")

logger = logging.getLogger(__name__)
_ = gettext.gettext

@app.command("all")
def get_all(
        ctx: typer.Context,
        query: str = typer.Option(None, help="Query parameters as key=value,key=value"),
            export: str = typer.Option(None, help="Export results to CSV file")):
    """
    Retrieve all locations from Trapper.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    query_dict = dict(item.split("=") for item in query.split(",")) if query else None
    results = trapper_client.classification_projects.get_all(query=query_dict)
    logger.info(f"Retrieved {len(results.results)} locations")
    logger.debug(results.model_dump_json(indent=4) )

    if export:
        trapper_client.export_list_to_csv(results, output_file=export)
    else:
        TyperUtils.json2Table(results, title="Classification Projects")

@app.command("id")
def get_by_id(
        ctx: typer.Context,
        deployment_id: str = typer.Argument(..., help=_("The unique ID of the classification to fetch"))
) -> None:
    """
    Get a deployment by its ID.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.classification_projects.get_by_id(deployment_id)
    TyperUtils.json2Table(result, columns=["id", "name", "locationID", "deploymentID"], title="Classification Projects")

@app.command("collection")
def get_by_collection(
    ctx: typer.Context,
    collection_id: str = typer.Argument(..., help=_("The unique ID of the collection whose classification projects will be fetched"))
) -> None:
    """
    Get deployments by location ID.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.deployments.classification_projects(collection_id)
    TyperUtils.json2Table(result, title="Classification Projects")
