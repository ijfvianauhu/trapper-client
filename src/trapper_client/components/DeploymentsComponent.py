import csv
from typing import TypeVar

from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr

@attr.s
class DeploymentsComponent(TrapperAPIComponent):
    """
    Component for interacting with the Deployments endpoint of the Trapper API.

    This component provides methods to retrieve deployment data, either individually
    or by applying filters such as acronym or associated location, and handles
    the mapping of API responses to Pydantic models.
    """

    explicit_fields = [
        "deployment_code",
        "deployment_id",
        "location",
        "research_project",
        "tags",
        "owner",
        "sdate_from",
        "sdate_to",
        "edate_from",
        "edate_to",
        "classification_project",
        "correct_setup",
        "correct_tstamp",
    ]

    def __attrs_post_init__(self):
        """
        Initialize the Deployments component.

        This method sets the endpoint and schema used to query and validate
        the API responses for deployments.
        """
        self._endpoint = "/geomap/api/deployments"
        self._schema = Schemas.TrapperDeploymentList

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
Auto-generated method for querying Deployments by field '{f}'.

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
        Retrieve a single deployment by its unique ID.

        Parameters
        ----------
        deployment_id : str
            The unique identifier of the deployment.

        Returns
        -------
        Schemas.TrapperDeploymentList
            A Pydantic model representing the deployment(s).

        Examples
        --------
        deployment = deployments_component.get_by_id("123")
        print(deployment.deploymentID)
        """

        return self.get_by_pk(pk, query)

    def get_by_acronym(self, deployment_acro: str, query: dict = None) -> T:
        """
        Retrieve deployments matching a specific acronym.

        Parameters
        ----------
        deployment_acro : str
            The acronym (deploymentID) used to filter deployments.

        Returns
        -------
        Schemas.TrapperDeploymentList
            A list or Pydantic model containing the matching deployment(s).

        Examples
        --------
        deployment = deployments_component.get_by_acronym("DEP_001")
        print(deployment)
        """
        return self.get_filtered(deploymentID=deployment_acro, query=query)


    def _get_by_location(self, location_id: str) -> T:
        """
        Retrieve deployments associated with a specific location.

        Parameters
        ----------
        location_id : str
            The ID of the location to filter deployments by.

        Returns
        -------
        Schemas.TrapperDeploymentList
            A list or Pydantic model containing the deployment(s) at the specified location.

        Examples
        --------
        deployments = deployments_component.get_by_location("LOC_001")
        for dep in deployments:
            print(dep.deploymentID)
        """
        return self.get_all(
            filter_fn=lambda dep: dep.locationID == location_id
        )

    def export(self, query: dict = None) -> None | csv.DictReader :
        return super().export(query=query,endpoint="/geomap/api/deployments/export/")
