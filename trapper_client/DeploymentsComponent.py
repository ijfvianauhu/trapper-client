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

    def __attrs_post_init__(self):
        """
        Initialize the Deployments component.

        This method sets the endpoint and schema used to query and validate
        the API responses for deployments.
        """
        self._endpoint = "/geomap/api/deployments/export/"
        self._schema = Schemas.TrapperDeploymentList

    def get_by_id(self, deployment_id: str) -> T:
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
        return self.get_all(
            filter_fn=lambda dep: dep.id == deployment_id
        )

    def get_by_acronym(self, deployment_acro: str) -> T:
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
        return self.get_all(
            filter_fn=lambda dep: dep.deploymentID == deployment_acro
        )

    def get_by_location(self, location_id: str) -> T:
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

