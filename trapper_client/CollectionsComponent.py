from typing import Dict, Any, Callable, TypeVar

from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr


#
# Collection
#

@attr.s
class CollectionsComponent(TrapperAPIComponent):
    """
    Component for interacting with Collections endpoint.

    Provides methods to retrieve and filter collections from the Trapper API.
    """

    def __attrs_post_init__(self):
        """
        Initialize the component with collections endpoint and schema.
        """
        self._endpoint = "/storage/api/collections"
        self._schema = Schemas.TrapperCollectionList

    def get_by_id(self, project_id: int) -> T:
        """
        Retrieve collection by ID.

        Parameters
        ----------
        project_id : int
            The ID of the collection.

        Returns
        -------
        T
            The collection with the specified vaID.
        """
        return self.get_all(query={"pk": project_id})

    def get_by_acronym(self, project_acro: str) -> T:
        """
        Retrieve collections by acronym.

        Parameters
        ----------
        project_acro : str
            The acronym or name to filter collections.

        Returns
        -------
        T
            Filtered collections matching the acronym.
        """

        return self.get_all(
            filter_fn=lambda dep: dep.name == project_acro
        )

    def get_by_research_project(self, project_id: int) -> T:
        """
        Retrieve collections associated with a research project.

        Parameters
        ----------
        project_id : int
            The ID of the research project.

        Returns
        -------
        Schemas.TrapperCollectionList
            Collections associated with the specified research project.
        """
        endpoint = f"/research/api/project/{project_id}/collections"
        res = self._client.get_all_pages(endpoint)
        return self._schema(**res)

    def get_by_classification_project(self, project_id: int) -> T:
        """
        Retrieve collections associated with a classification project.

        Parameters
        ----------
        project_id : int
            The ID of the classification project.

        Returns
        -------
        Schemas.TrapperCollectionList
            Collections associated with the specified classification project.
        """
        endpoint = f"/media_classification/api/project/{project_id}/collections"
        res = self._client.get_all_pages(endpoint)
        return self._schema(**res)
