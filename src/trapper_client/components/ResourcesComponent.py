from typing import Dict, Any, Callable, TypeVar

from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr

@attr.s
class ResourcesComponent(TrapperAPIComponent):
    """
    Component for interacting with Resources endpoint.

    Provides methods to retrieve resources associated with collections or locations.
    """

    explicit_fields = [
        "name",
        "resource_type",  # ChoiceFilter
        "status",  # ChoiceFilter
        "rdate_from",  # BaseDateFilter sobre date_recorded__date (gte)
        "rdate_to",  # BaseDateFilter sobre date_recorded__date (lte)
        "udate_from",  # BaseDateFilter sobre date_uploaded__date (gte)
        "udate_to",  # BaseDateFilter sobre date_uploaded__date (lte)
        "rtime_from",  # BaseTimeFilter sobre date_recorded (gte)
        "rtime_to",  # BaseTimeFilter sobre date_recorded (lte)
        "owner",  # OwnResourceBooleanFilter
        "locations_map",  # BaseLocationsMapFilter sobre deployment__location
        "collections",  # MultipleChoiceFilter
        "deployments",  # CharFilter, método get_deployments
        "deployment__isnull",  # BooleanFilter
        "tags",  # MultipleChoiceFilter
        "observation_type",  # CharFilter, método get_observation_type
        "species",  # CharFilter, método get_species
        "timestamp_error",  # BooleanFilter, método get_timestamp_error
    ]

    def __attrs_post_init__(self):
        """
        Initialize the component with resources endpoint and schema.
        """
        self._endpoint = "/storage/api/resources"
        self._schema = Schemas.TrapperResourceList

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
Auto-generated method for querying Resources by field '{f}'.

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

    def get_by_collection(self, cp_id: int, query: dict = None) -> T:
        """
        Retrieve resources from a specific collection.

        Parameters
        ----------
        cp_id : int
            The ID of the collection (replaces {pk} in the endpoint).
        query : dict, optional
            Optional search/pagination parameters.

        Returns
        -------
        Schemas.TrapperResourceList
            Resources associated with the specified collection.
        """
        res = self._client.get_all_pages(f"/storage/api/resources/collection/{cp_id}", query)
        return self._schema(**res)

    def get_by_location(self, cp_id: int, query: dict = None) -> T:
        """
        Retrieve resources from a specific location.

        Parameters
        ----------
        cp_id : int
            The ID of the location.
        query : dict, optional
            Optional search/pagination parameters.

        Returns
        -------
        Schemas.TrapperResourceList
            Resources associated with the specified location.
        """
        endpoint = f"/storage/api/resources/location/{cp_id}"
        res = self._client.get_all_pages(endpoint, query)

        return self._schema(**res)
