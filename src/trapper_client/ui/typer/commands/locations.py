import typer, logging,gettext
from trapper_client.TrapperClient import TrapperClient
from trapper_client.ui.typer.TyperUtils import TyperUtils

app = typer.Typer(help="Manage Locations")

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
    results = trapper_client.locations.get_all(query=query_dict)
    logger.info(f"Retrieved {len(results.results)} locations")
    logger.debug(results.model_dump_json(indent=4) )

    if export:
        client.export_list_to_csv(results, output_file=export)
    else:
        TyperUtils.json2Table(results)

@app.command("id")
def get_by_id(
        ctx: typer.Context,
        location_id: str = typer.Argument(..., help=_("The unique ID of the location to fetch"))
) -> None:
    """
    Get a location by its ID.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]
    results = trapper_client.locations.get_by_id(location_id)
    TyperUtils.json2Table(results)

@app.command("acronym")
def get_by_acronym(
        ctx: typer.Context,
        acronym: str = typer.Argument(..., help=_("The acronym of the location to fetch"))
) -> None:
    """
    Get a location by its acronym.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.locations.get_by_acronym(acronym)
    TyperUtils.json2Table(result)

@app.command("project")
def get_by_research_project(
        ctx: typer.Context,
        project_id: str = typer.Argument(..., help=_("The unique ID of the project whose locations will be fetched"))
) -> None:
    """
    Get locations by research project ID.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.locations.get_by_research_project(project_id)
    TyperUtils.json2Table(result)
