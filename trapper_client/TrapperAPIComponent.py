from typing import Type, Dict, Any, Callable, TypeVar

from trapper_client.APIClientBase import APIClientBase
import attr

T = TypeVar("T")

@attr.s
class TrapperAPIComponent:
    """
    Base component for interacting with Trapper API endpoints.

    This class defines the core methods and attributes that other API components
    inherit from, including handling queries and filtering results.

    Attributes
    ----------
    _client : APIClientBase
        The API client used for making HTTP requests
    _endpoint : str
        The API endpoint URL for this component
    _schema : Type[T]
        The Pydantic schema class for response validation
    """

    _client: APIClientBase = attr.ib(repr=False)
    _endpoint: str = attr.ib(init=False)
    _schema: Type[T] = attr.ib(init=False)

    def get_all(self, query: Dict[str, Any] = None, filter_fn: Callable[[T], bool] = None) -> T:
        """
        Retrieve all results from the endpoint.

        This method fetches all items from the API endpoint. Optionally, you can provide
        query parameters to filter the request on the server side and/or a Python function
        to filter the results locally.

        Parameters
        ----------
        query : dict[str, Any], optional
            A dictionary of query parameters to send with the request. Defaults to None.
            Example: {"status": "active", "page_size": 100}

        filter_fn : Callable[[T], bool], optional
            A callable (e.g., lambda function) that receives each item and returns True
            if the item should be included in the final result. Defaults to None.
            Example: `lambda item: item.status == "active"`

        Returns
        -------
        T
            A list or a Pydantic model containing all retrieved items. The type depends on
            the endpoint being accessed.
        """
        res = self._client.get_all_pages(self._endpoint, query)
        parsed = self._schema(**res)

        if filter_fn:
            parsed.results = [r for r in parsed.results if filter_fn(r)]

        return parsed
