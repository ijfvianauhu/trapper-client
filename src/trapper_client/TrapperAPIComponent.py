import csv
import io
import zipfile
from typing import Type, Dict, Any, Callable, TypeVar
from trapper_client.APIClientBase import APIClientBase
import attr

T = TypeVar("T")

@attr.s
class TrapperAPIComponent:
    """
    Base component for interacting with Trapper API endpoints.

    This class defines core methods and attributes that other API components
    inherit from, including handling queries and filtering results.

    Attributes
    ----------
    _client : APIClientBase
        The API client used for making HTTP requests.
    _endpoint : str
        The API endpoint URL for this component (initialized in subclass).
    _schema : Type[T]
        The Pydantic schema class for response validation (initialized in subclass).
    explicit_fields : list[str]
        Fields for which automatic getter methods are generated. Subclasses can
        extend this list.

    Notes
    -----
    For each field in `explicit_fields`, the class automatically generates:

    - get_by_<field>(value, query=None, filter_fn=None, endpoint=None)
        Retrieves filtered results for a single page.
    - get_all_by_<field>(value, query=None, filter_fn=None, endpoint=None)
        Retrieves filtered results from all pages.

    Common query parameters supported by the API:
        - search: global search in text fields, e.g., ?search=lynx
        - ordering: sort results, e.g., ?ordering=-date_created
        - page: page number (pagination)
        - page_size: number of items per page
        - filter_fn: optional callable to filter results locally
    """

    _client: APIClientBase = attr.ib(repr=False)
    _endpoint: str = attr.ib(init=False)
    _schema: Type[T] = attr.ib(init=False)

    explicit_fields = ["pk"]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        #if "__init_subclass__" in cls.__dict__:
        #    # Es una clase que redefine este método -> no generamos métodos automáticos
        #    return
        # Evitar generar métodos automáticos solo si la clase es MediaComponent
        if cls.__name__ == "MediaComponent":
            return

        # Combina explicit_fields de todas las clases padre con los nuevos
        base_fields = []
        for base in cls.__mro__[1:]:
            base_fields.extend(getattr(base, "explicit_fields", []))
        new_fields = getattr(cls, "explicit_fields", [])
        cls.explicit_fields = list(dict.fromkeys(base_fields + new_fields))

        # Genera métodos get_by_<field> y get_all_by_<field>
        for field in cls.explicit_fields:

            def make_getter(f, all_results=False):
                prefix = "get_all_by_" if all_results else "get_by_"
                method_name = f"{prefix}{f}"

                def getter(self, value, query=None, filter_fn=None, endpoint=None):
                    """
                    Auto-generated method for querying by field '{f}'.

                    Parameters
                    ----------
                    value : Any
                        Value to filter by for field '{f}'.
                        If a list is provided, it will be joined by commas.
                    query : dict, optional
                        Additional query parameters.
                    filter_fn : callable, optional
                        Local filter function applied after fetching results.
                    endpoint : str, optional
                        Optional endpoint override.

                    Returns
                    -------
                    T
                        Filtered results from the API.
                    """
                    query = query or {}
                    if isinstance(value, list):
                        value = ",".join(map(str, value))
                    query[f] = value
                    if all_results:
                        return self.get_all(query, filter_fn=filter_fn, endpoint=endpoint)
                    return self.get(query, filter_fn=filter_fn, endpoint=endpoint)

                getter.__name__ = method_name
                getter.__doc__ = getter.__doc__.format(f=f)
                return getter

            setattr(cls, f"get_by_{field}", make_getter(field, all_results=False))
            setattr(cls, f"get_all_by_{field}", make_getter(field, all_results=True))

    def get_all(
        self,
        query: Dict[str, Any] = None,
        filter_fn: Callable[[T], bool] = None,
        endpoint: str = None,
    ) -> T:
        """
        Retrieve all results (all pages) from the endpoint.

        Parameters
        ----------
        query : dict[str, Any], optional
            Dictionary of query parameters to send with the request.
        filter_fn : Callable[[T], bool], optional
            Optional function to filter results locally.
        endpoint : str, optional
            Optional endpoint override.

        Returns
        -------
        T
            Pydantic model containing all retrieved results.
        """
        actual_endpoint = endpoint or self._endpoint
        res = self._client.get_all_pages(actual_endpoint, query)
        parsed = self._schema(**res)
        if filter_fn:
            parsed.results = [r for r in parsed.results if filter_fn(r)]
        return parsed

    def get(
        self,
        query: Dict[str, Any] = None,
        filter_fn: Callable[[T], bool] = None,
        endpoint: str = None,
    ) -> T:
        """
        Retrieve results from the endpoint (single page).

        Parameters
        ----------
        query : dict[str, Any], optional
            Dictionary of query parameters to send with the request.
        filter_fn : Callable[[T], bool], optional
            Optional function to filter results locally.
        endpoint : str, optional
            Optional endpoint override.

        Returns
        -------
        T
            Pydantic model containing retrieved results.
        """
        actual_endpoint = endpoint or self._endpoint
        res = self._client.get(actual_endpoint, query)
        parsed = self._schema(**res)
        if filter_fn:
            parsed.results = [r for r in parsed.results if filter_fn(r)]
        return parsed

    def get_all_filtered(
        self,
        *,
        filter_fn: Callable[[T], bool] = None,
        endpoint: str = None,
        **filters
    ) -> T:
        """
        Retrieve results applying the given filters to all pages.

        Parameters
        ----------
        filter_fn : Callable[[T], bool], optional
            Optional local filter function.
        endpoint : str, optional
            Optional endpoint override.
        **filters : dict
            Keyword arguments for fields to filter by.

        Returns
        -------
        T
            Filtered results.
        """
        return self.get_all(filters, filter_fn=filter_fn, endpoint=endpoint)

    def get_filtered(
        self,
        *,
        filter_fn: Callable[[T], bool] = None,
        endpoint: str = None,
        **filters
    ) -> T:
        """
        Retrieve results applying the given filters (single page).

        Parameters
        ----------
        filter_fn : Callable[[T], bool], optional
            Optional local filter function.
        endpoint : str, optional
            Optional endpoint override.
        **filters : dict
            Keyword arguments for fields to filter by.

        Returns
        -------
        T
            Filtered results.
        """
        return self.get(filters, filter_fn=filter_fn, endpoint=endpoint)

    def export(self,query: Dict[str, Any] = None, endpoint: str = None) -> None | csv.DictReader :
        a= self._client.make_request(
            method="GET",
            endpoint=endpoint,
            query=query,
            only_json=False
        )

        content_type = a.headers.get("Content-Type", "")

        if "text/csv" in content_type or a.text.strip().startswith(
            tuple("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")):

            if a.content[:4] == b'PK\x03\x04' or "zip" in content_type:
                with zipfile.ZipFile(io.BytesIO(a.content)) as zf:
                    csv_name = next((n for n in zf.namelist() if n.endswith(".csv")), None)
                    csv_text = zf.read(csv_name).decode("utf-8") if csv_name else ""
            elif a.content[:2] == b'\x1f\x8b' or "gzip" in content_type:
                import gzip
                csv_text = gzip.decompress(a.content).decode("utf-8")
            elif a.content[:2] == b'BZ' or "bzip2" in content_type:
                import bz2
                csv_text = bz2.decompress(a.content).decode("utf-8")
            else:
                csv_text = a.text

            return csv.DictReader(io.StringIO(csv_text))
        else:
            None