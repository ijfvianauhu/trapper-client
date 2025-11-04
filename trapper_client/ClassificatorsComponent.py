from typing import Dict, Any, Callable, TypeVar

from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr

@attr.s
class ClassificatorsComponent(TrapperAPIComponent):
    """
    Component for interacting with the Classificators endpoint of the Trapper API.

    This component provides methods to retrieve location data, either individually
    or in bulk, and handles the mapping of API responses to Pydantic models.
    """

    def __attrs_post_init__(self):
        """
        Initialize the Locations component.

        This method sets the endpoint and schema used to query and validate
        the API responses for locations.
        """
        self._endpoint = "/media_classification/api/classificators"
        self._schema = Schemas.TrapperClassificatorList

    def get_by_id(self, location_id: str) -> T:
        """
        Retrieve a single classificator by its ID.

        Parameters
        ----------
        location_id : str
            The unique identifier of the location to retrieve.

        Returns
        -------
        Schemas.TrapperLocationLis
            A Pydantic model representing the location.

        Examples
        --------
        # Fetch a location by ID
        location = locations_component.get_by_id("216")
        print(location.name)
        """
        return self.get_all(
            filter_fn=lambda dep: dep.pk == location_id
        )

    def get_by_name(self, location_acro: str) -> T:
        """
        Retrieve classificators matching a specific name.

        This method fetches all locations and applies a local filter to return
        only those whose `locationID` matches the provided acronym.

        Parameters
        ----------
        location_acro : str
            The acronym (locationID) used to filter locations.

        Returns
        -------
        Schemas.TrapperLocationList
            A list or Pydantic model containing the matching location(s).

        Examples
        --------
        # Fetch a location with acronym "WICP_0002"
        location = locations_component.get_by_acronym("WICP_0002")
        print(location)
        """
        return self.get_all(
            filter_fn=lambda dep: dep.name == location_acro
        )

