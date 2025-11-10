from typing import Dict, Any, Callable, TypeVar, List

from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr

from trapper_client.components.CollectionsComponent import CollectionsComponent


@attr.s
class ResearchProjectsComponent(TrapperAPIComponent):
    """
    Retrieve classification projects associated with a specific collection.

    Parameters
    ----------
    collection_id : str
        The ID of the collection to filter classification projects.

    Returns
    -------
    Schemas.TrapperClassificationProjectList
        Classification projects associated with the specified collection.
    """

    explicit_fields = [
#        "owner",
        "keywords",
        "acronym",
    ]

    def __attrs_post_init__(self):
        """
        Initialize the component with research projects endpoint and schema.
        """
        self._endpoint = "/research/api/projects"
        self._schema = Schemas.TrapperResearchProjectList

    def __init_subclass__(cls, **kwargs):
        """
        Dynamically generates getter methods with docstrings
        for each explicit field when the subclass is created.
        """
        super().__init_subclass__(**kwargs)

        for field in cls.explicit_fields:

            def make_getter(f, all_results=False):
                prefix = "get_all_by_" if all_results else "get_by_"
                method_name = f"{prefix}{f}"

                doc = f"""
Auto-generated method for querying Research Project by field '{f}'.

Parameters
----------
value : Any
    Value to filter by for field '{f}'. Can be a single value or a list
    (lists will be joined by commas).
query : dict, optional
    Additional query parameters to include.
filter_fn : callable, optional
    Optional function to filter results locally after fetching.
endpoint : str, optional
    Optional endpoint override.

Returns
-------
T
    A Pydantic model containing the filtered results.
"""

                def getter(self, value, query=None, filter_fn=None, endpoint=None):
                    query = query or {}
                    if isinstance(value, list):
                        value = ",".join(map(str, value))
                    query[f] = value
                    if all_results:
                        return self.get_all(query, filter_fn=filter_fn, endpoint=endpoint)
                    return self.get(query, filter_fn=filter_fn, endpoint=endpoint)

                getter.__name__ = method_name
                getter.__doc__ = doc
                return getter

            setattr(cls, f"get_by_{field}", make_getter(field, all_results=False))
            setattr(cls, f"get_all_by_{field}", make_getter(field, all_results=True))


    def get_by_id(self, pk: int, query: dict = None) -> T:
        """
        Retrieve research project by ID.

        Parameters
        ----------
        project_id : int
            The ID of the research project.

        Returns
        -------
        T
            The research project with the specified ID.
        """
        return self.get_by_pk(pk, query)

    def get_by_collection(self, collection_id: int) -> T:
        """
        Retrieve research projects associated with a specific collection.

        Parameters
        ----------
        collection_id : int
            The ID of the collection to filter research projects.

        Returns
        -------
        Schemas.TrapperResearchProjectList
            Research projects associated with the specified collection.
        """
        rps = self.get_all()
        result = []
        for cp in rps.results:
            collections = CollectionsComponent(self._client).get_by_research_project(int(cp.pk))
            found = any(int(c.collection_pk) == int(collection_id) for c in collections.results)
            if found:
                result.append(cp)

        pagination = rps.pagination
        pagination.count = len(result)

        return Schemas.TrapperResearchProjectList(**{"pagination": pagination, "results": result})

    def get_by_owner(self, owner: str) -> T:
        """
        Retrieve research projects by owner.

        Parameters
        ----------
        owner : str
            The owner username to filter research projects.

        Returns
        -------
        T
            Research projects owned by the specified user.
        """
        return self.get_all(
            filter_fn=lambda dep: dep.owner == owner
        )

    def get_by_owners(self, owners: List[str]) -> T:
        """
        Retrieve research projects by owner.

        Parameters
        ----------
        owner : str
            The owner username to filter research projects.

        Returns
        -------
        T
            Research projects owned by the specified user.
        """
        return self.get_all(
            filter_fn=lambda dep: dep.owner in owners
        )

    def get_my(self, username="me") -> T:
        """
        Retrieve research projects associated with the current user.

        Parameters
        ----------
        username : str, optional
            The username to filter by. Defaults to "me" for current user.

        Returns
        -------
        T
            Research projects where the user is owner or has specific roles.
        """
        if username == "me":
            username = self._client.user_name
        roles = ["Admin", "Collaborator", "Expert"]

        return self.get_all(
            filter_fn=lambda proj: (
                    (username and proj.owner == username)
                    or (
                            username
                            and any(
                        role.username == username and any(r in roles for r in role.roles)
                        for role in proj.project_roles
                    )
                    )
            )
        )
