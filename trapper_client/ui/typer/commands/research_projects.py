import typer, logging,gettext
from trapper_client.TrapperClient import TrapperClient
from trapper_client.ui.typer.TyperUtils import TyperUtils

app = typer.Typer(help="Manage Research Projects")

logger = logging.getLogger(__name__)
_ = gettext.gettext

@app.command("all",
    short_help=_("Retrieve all research projects based on optional query parameters"),
    help=_("This command allows users to fetch research projects from the database. Query parameters can be provided to filter results, and the output can optionally be exported to a CSV file.")
)
def get_all(
        ctx: typer.Context,
        query: str = typer.Option(None, help="Query parameters as key=value,key=value"),
        export: str = typer.Option(None, help="Export results to CSV file")) -> None:
    """
    Retrieve all research projects based on optional query parameters.

    This command allows users to fetch research projects from the database.
    Query parameters can be provided to filter results, and the output can
    optionally be exported to a CSV file.

    Args:
        ctx (typer.Context): The Typer context object, used to share information across commands.
        query (str, optional): Query parameters in the format `key=value,key=value` to filter projects.
        export (str, optional): Path to a CSV file where the results will be exported.

    Returns:
        None: Prints the research projects  details to the CLI output or to csv file.

    """

    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    query_dict = dict(item.split("=") for item in query.split(",")) if query else None
    results = trapper_client.research_projects.get_all(query=query_dict)
    logger.info(f"Retrieved {len(results.results)} research projects")
    logger.debug(results.model_dump_json(indent=4) )

    if export:
        trapper_client.export_list_to_csv(results, output_file=export)
    else:
        TyperUtils.json2Table(results, title="Research Projects", columns=["pk", "acronym", "name", "owner", "keywords"])

@app.command("id",
    short_help=_("Retrieve a specific research project classification by its unique ID."),
    help=_("This command fetches detailed information about a single classification associated with a research project, based on the provided deployment ID.")
)
def get_by_id(
        ctx: typer.Context,
        rp_id: str = typer.Argument(..., help=_("The unique ID of the classification to fetch"))
) -> None:
    """
    Retrieve a specific research project classification by its unique ID.

    This command fetches detailed information about a single classification
    associated with a research project, based on the provided deployment ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        rp_id (str): The unique identifier of the reseach project to retrieve.

    Returns:
        None: Prints the research project details to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.research_projects.get_by_id(rp_id)
    if len(result.results) > 0:
        TyperUtils.print_pydantic_card(result.results[0], title=f"Research Project {rp_id}")

@app.command("collection",
    short_help=_("Retrieve all research projects associated with a specific collection."),
    help=_("This command fetches research projects that belong to a collection identified by its unique collection ID.")
)
def get_by_collection(
    ctx: typer.Context,
    collection_id: str = typer.Argument(..., help=_("The unique ID of the collection whose research projects will be fetched"))
) -> None:
    """
    Retrieve all research projects associated with a specific collection.

    This command fetches research projects that belong to a collection identified
    by its unique collection ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        collection_id (str): The unique ID of the collection whose research
            projects will be retrieved.

    Returns:
        None: Prints the list of research projects to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.research_projects.get_by_collection(collection_id)
    TyperUtils.json2Table(result, title=f"Research Projects which use the collection {collection_id}", columns=["pk", "acronym", "name", "owner", "keywords"])

@app.command("acronym",
    short_help=_("Retrieve a research project based on its acronym."),
    help=_("This command fetches detailed information about a research project using the provided acronym to identify it.")
)
def get_by_acronym(
    ctx: typer.Context,
    acronym: str = typer.Argument(..., help=_("The acronym of the research project we are interested in"))
) -> None:
    """
    Retrieve a research project based on its acronym.

    This command fetches detailed information about a research project
    using the provided acronym to identify it.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        acronym (str): The acronym of the research project of interest.

    Returns:
        None: Prints the project details to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.research_projects.get_by_acronym(acronym)
    TyperUtils.json2Table(result, title=f"Research Projects with acronym {acronym}", columns=["pk", "acronym", "name", "owner", "keywords"])

@app.command("owner",
    short_help=_("Retrieve all research projects owned by a specific user."),
    help=_("This command fetches the research project classifications that belong to a user identified by their username."))
def get_by_owner(
        ctx: typer.Context,
        owner: str = typer.Argument(..., help=_(
            "The username of the user whose research projects we want to retrieve"))
) -> None:
    """
    Retrieve all research projects owned by a specific user.

    This command fetches the research project classifications that belong
    to a user identified by their username.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        owner (str): The username of the user whose classification projects
            should be retrieved.

    Returns:
        None: Prints the list of classification projects to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.research_projects.get_by_owner(owner)
    TyperUtils.json2Table(result, title=f"Research Projects whose owner is {owner}", columns=["pk", "acronym", "name", "owner", "keywords"])

@app.command("my",
    short_help=_("Retrieve all research projects in which a user may attempt to participate"),
    help=_("This command fetches the research project associated with a given user, identified by its unique user ID")
)
def my(
        ctx: typer.Context,
        owner: str = typer.Argument(..., help=_(
            "The unique ID of the collection whose classification projects will be fetched"))
) -> None:
    """"
    Retrieve all research projects in which a user may attempt to participate.

    This command fetches the research project associated with a given user, identified by its unique user ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        owner (str): The unique ID of the user whose research
            projects will be retrieved.

    Returns:
        None: Prints the list of research projects to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.research_projects.get_my(owner)
    TyperUtils.json2Table(result, title=f"My Research Projects", columns=["pk", "acronym", "name", "owner", "keywords", "project_roles"])