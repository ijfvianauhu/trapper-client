from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr

@attr.s
class ClassificatorsComponent(TrapperAPIComponent):
    """
    Component for interacting with the **Classificators** endpoint of the Trapper API.

    This component provides methods to retrieve and filter *Classificator* objects
    from the Trapper backend. It handles the endpoint configuration and mapping
    of API responses into Pydantic schema models.

    The available query parameters for filtering *Classificators* are listed below.

    **Filterable Fields**

    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | **Field**                                  | **Type**                   | **Description**                                               |
    +============================================+============================+===============================================================+
    | ``pk``                                     | AutoField (PK)             | Unique identifier of the classificator                        |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``name``                                   | CharField                 | Unique name of the classificator                              |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``owner``                                  | ForeignKey → User         | Owner of the classificator; can be filtered via ``owner`` or  |
    |                                            |                            | ``owners`` (multiple)                                         |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``template``                               | CharField (choices)       | Template type (e.g., ``inline``)                              |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``species``                                | ManyToManyField → Species | Associated species                                            |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``tracked_species``                        | ManyToManyField → Species | Explicitly tracked species                                    |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``observation_type``                       | BooleanField              | Whether it includes the observation type                      |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``is_setup``                               | BooleanField              | Indicates if it is a setup classificator                      |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``sex``                                   | BooleanField              | Whether it includes the sex attribute                         |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``age``                                   | BooleanField              | Whether it includes the age attribute                         |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``count``                                 | BooleanField              | Whether it includes the count attribute                       |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``count_new``                             | BooleanField              | Whether it includes the “count new” attribute                 |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``behaviour``                             | BooleanField              | Whether it includes the behaviour attribute                   |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``individual_id``                         | BooleanField              | Whether it includes the individual ID attribute               |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``classification_confidence``             | BooleanField              | Whether it includes the classification confidence attribute   |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+
    | ``updated_date (udate_from / udate_to)``  | DateTimeField             | Last update date, filterable by range (``gte`` / ``lte``)     |
    +--------------------------------------------+----------------------------+---------------------------------------------------------------+

    **Example**

    .. code-block:: python

        from trapper_client import TrapperClient

        client = TrapperClient()
        classificators = client.classificators.get_all(
            query={"name": "Wildlife_Project_A"}
        )

        for c in classificators:
            print(c.name, c.owner.username)

    **Endpoint**
        ``/media_classification/api/classificators``

    **Schema**
        :class:`Schemas.TrapperClassificatorList`
    """

    explicit_fields = [
        "name",
        "owner",
        "template", # inline, upload, etc.
        "species", # all species
        "tracked_species",
        "observation_type",
        "is_setup",
        "sex",
        "age",
        "count",
        "count_new",
        "behaviour",
        "individual_id",
        "classification_confidence",
        "updated_date",
    ]

    def __attrs_post_init__(self):
        """
        Initialize the Locations component.

        This method sets the endpoint and schema used to query and validate
        the API responses for locations.
        """
        self._endpoint = "/media_classification/api/classificators"
        self._schema = Schemas.TrapperClassificatorList

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
Auto-generated method for querying Classificators by field '{f}'.

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

    def get_by_id(self, pk: str, query: dict = None) -> T:
        """
        Retrieve a single classificator by its unique identifier.

        This method queries the API and returns the classificator
        whose primary key (``pk``) matches the provided value.
        Internally, it fetches all classificators and applies a
        client-side filter using the given ID.

        :param pk:
            The unique identifier (primary key) of the classificator to retrieve.
        :type pk: str

        :param query:
            Optional dictionary of query parameters for the request.
        :type query: dict, optional

        :returns:
            A Pydantic model instance representing the requested classificator.
        :rtype: Schemas.TrapperClassificatorList

        **Example**

        .. code-block:: python

            from trapper_client import TrapperClient

            client = TrapperClient()
            classificator = client.classificators.get_by_id("216")
            print(classificator.name)
        """

        return self.get_by_pk(pk,query)

    def get_by_name(self, name: str, query: dict = None) -> T:
        """
        Retrieve classificators that match a given name.

        This method fetches all classificators and filters them locally,
        returning only those whose ``name`` field matches the specified value.

        :param name:
            The classificator name used for filtering.
        :type name: str

        :param query:
            Optional dictionary of query parameters for the request.
        :type query: dict, optional

        :returns:
            A list or Pydantic model representing the classificators
            that match the given name.
        :rtype: Schemas.TrapperClassificatorList

        **Example**

        .. code-block:: python

            from trapper_client import TrapperClient

            client = TrapperClient()
            classificators = client.classificators.get_by_name("WildINTEL_2025")
            for c in classificators:
                print(c.name)
        """

        return self.get_by_name(name,query)

    def get_by_owner(self, owner: str = None, query: dict = None) -> T:
        """
        Retrieve classificators that match a given owner.

        This method fetches all classificators and filters them locally,
        returning only those whose ``name`` field matches the specified value.

        :param owner:
            The owner name used for filtering.
        :type owner: str

        :param query:
            Optional dictionary of query parameters for the request.
        :type query: dict, optional

        :returns:
            A list or Pydantic model representing the classificators
            that match the given name.
        :rtype: Schemas.TrapperClassificatorList

        **Example**

        .. code-block:: python

            from trapper_client import TrapperClient

            client = TrapperClient()
            classificators = client.classificators.get_by_owner("WildINTEL_2025")
            for c in classificators:
                print(c.name)
        """
        if owner is None:
            owner = self._client.user_name
        query = query or {}

        query["owner"] = owner

        return self.get_all(query)

