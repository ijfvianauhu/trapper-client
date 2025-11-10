import csv
import io
import zipfile
from typing import List, Any
from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr

@attr.s
class LocationsComponent(TrapperAPIComponent):
    """
    Component for interacting with the Locations endpoint of the Trapper API.

    This component provides methods to retrieve location data, either individually
    or in bulk, and handles the mapping of API responses to Pydantic models.

    Attributes
    ----------
    explicit_fields : list[str]
        Fields for which automatic getter methods are generated:
        - name
        - description
        - owner
        - owners
        - research_project
        - deployments
        - locations_map
    """

    explicit_fields = [
        "name",
        "location_id",
        "description",
        "owner",
        "owners",
        "research_project",
        "deployments",
        "locations_map",
        "is_public",
        "city",
        "country",
        "state",
        "county"
    ]

    def __attrs_post_init__(self):
        """
        Initialize the Locations component.

        Sets the endpoint and schema used to query and validate
        the API responses for locations.
        """
        self._endpoint = "/geomap/api/locations"
        self._schema = Schemas.TrapperLocationList

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
Auto-generated method for querying Locations by field '{f}'.

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

    # Métodos explícitos
    def get_by_id(self, pk: str, query: dict = None) -> T:
        """
        Retrieve a single location by its primary key.

        Parameters
        ----------
        pk : str
            The unique identifier (primary key) of the location.
        query : dict, optional
            Additional query parameters.

        Returns
        -------
        T
            A Pydantic model representing the location.
        """
        return self.get_by_pk(pk, query)

    def get_by_acronym(self, acro: str, query: dict = None) -> T:
        """
        Retrieve locations matching a specific acronym (location_id).

        Parameters
        ----------
        acro : str
            The acronym or location_id used to filter locations.
        query : dict, optional
            Additional query parameters.

        Returns
        -------
        T
            A Pydantic model or list of matching locations.
        """
        return self.get_filtered(location_id=acro, query=query)

    def export(self, query: dict = None) -> None | csv.DictReader :
        return super().export(query=query,endpoint="/geomap/api/locations/export/")
