from typing import Set

from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent
from trapper_client.components.CollectionsComponent import CollectionsComponent
from trapper_client.TrapperAPIComponent import T
import attr

@attr.s
class ClassificationProjectsComponent(TrapperAPIComponent):
    """
    Component for interacting with the Classification Projects endpoint of the Trapper API.

    :cvar explicit_fields: List of fields for which automatic getter methods are generated.
    :type explicit_fields: list[str]

    **Examples:**

    .. code-block:: python

        from trapper_client.components.ClassificationProjectsComponent import ClassificationProjectsComponent

        # Initialize component
        cp_component = ClassificationProjectsComponent(client)

        # Retrieve a single project by ID
        project = cp_component.get_by_id(123)
        print(project.results[0].name)

        # Retrieve all projects with a specific owner
        owner_projects = cp_component.get_by_owner("john_doe")
        for p in owner_projects.results:
            print(p.pk, p.name)

        # Retrieve all projects with a given status
        ongoing_projects = cp_component.get_by_status("ONGOING")
        for p in ongoing_projects.results:
            print(p.pk, p.status)

        # Retrieve all projects in a specific research project
        research_projects = cp_component.get_by_research_project(45)
        for p in research_projects.results:
            print(p.pk, p.research_project)

        # Retrieve all projects associated with a specific collection
        collection_projects = cp_component.get_by_collection("77")
        for p in collection_projects.results:
            print(p.pk, p.name)

        # Retrieve all projects matching a field, multiple results
        all_by_status = cp_component.get_all_by_status("FINISHED")
        for p in all_by_status.results:
            print(p.pk, p.status)

        # Filter locally using the optional filter_fn
        custom_filter = cp_component.get_all_by_owner("john_doe", filter_fn=lambda cp: cp.status == "ONGOING")
        for p in custom_filter.results:
            print(p.pk, p.name)
    """

    explicit_fields = [
        "pk",
        "owner",
        "research_project",
        "status",
    ]

    def __attrs_post_init__(self):
        """
        Initialize the component with endpoint and schema.
        """
        self._endpoint = "/media_classification/api/projects"
        self._schema = Schemas.TrapperClassificationProjectList

    def __init_subclass__(cls, **kwargs):
        """
        Dynamically generate getter methods for each explicit field when the subclass is created.
        """
        super().__init_subclass__(**kwargs)

        for field in cls.explicit_fields:

            def make_getter(f, all_results=False):
                prefix = "get_all_by_" if all_results else "get_by_"
                method_name = f"{prefix}{f}"

                doc = f"""
Auto-generated method for querying Classification Projects by field ``{f}``.

:param value: Value to filter by for field ``{f}``. Can be a single value or a list (lists will be joined by commas).
:type value: Any
:param query: Additional query parameters to include.
:type query: dict, optional
:param filter_fn: Optional function to filter results locally after fetching.
:type filter_fn: callable, optional
:param endpoint: Optional endpoint override.
:type endpoint: str, optional

:returns: A Pydantic model containing the filtered results.
:rtype: T
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
        Retrieve a single classification project by its unique ID.

        :param pk: The unique identifier of the classification project.
        :type pk: int
        :param query: Optional query parameters.
        :type query: dict, optional
        :returns: A Pydantic model representing the classification project(s).
        :rtype: Schemas.TrapperClassificationProjectList
        """
        return self.get_pk(pk, query)

    def get_by_name(self, name: str, query: dict = None) -> T:
        """
        Retrieve classification projects by acronym or name.

        :param name: The acronym or name to filter classification projects.
        :type name: str
        :param query: Optional query parameters.
        :type query: dict, optional
        :returns: Filtered classification projects whose name matches the acronym.
        :rtype: T
        """
        return self.get_all(query, filter_fn=lambda dep: dep.name == name)

    def get_by_owners(self, owners: Set[str], query: dict = None) -> T:
        """
        Retrieve classification projects owned by specific users.

        :param owners: Set of usernames or identifiers of owners.
        :type owners: Set[str]
        :param query: Optional query parameters.
        :type query: dict, optional
        :returns: Classification projects owned by the specified users.
        :rtype: Schemas.TrapperClassificationProjectList
        """
        return self.get_all(query, filter_fn=lambda cp: cp.owner in owners)

    def get_by_collection(self, collection_id: str, query: dict = None) -> T:
        """
        Retrieve classification projects associated with a specific collection.

        :param collection_id: The ID of the collection to filter classification projects.
        :type collection_id: str
        :param query: Optional query parameters.
        :type query: dict, optional
        :returns: Classification projects associated with the specified collection.
        :rtype: Schemas.TrapperClassificationProjectList
        """
        cps = self.get_all()
        result = []
        for cp in cps.results:
            collections = CollectionsComponent(self._client).get_by_classification_project(int(cp.pk), query)
            found = any(c.collection_pk == collection_id for c in collections.results)
            if found:
                result.append(cp)

        pagination = cps.pagination
        pagination.count = len(result)

        return Schemas.TrapperClassificationProjectList(**{"pagination": pagination, "results": result})
