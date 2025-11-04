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

    def __attrs_post_init__(self):
        """
        Initialize the component with resources endpoint and schema.
        """
        self._endpoint = "/storage/api/resources/collection/{pk}"
        self._schema = Schemas.TrapperResourceList

    def get_all(self, query: Dict[str, Any] = None, filter_fn: Callable[[T], bool] = None) -> T:
        self._endpoint = "/storage/api/resources"
        return super().get_all(query, filter_fn)

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
        endpoint = self._endpoint.format(pk=cp_id)
        res = self._client.get_all_pages(endpoint, query)
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
