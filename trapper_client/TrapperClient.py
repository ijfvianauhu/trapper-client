import sys
from collections import defaultdict
from pathlib import Path
from typing import TypeVar, Type, Dict, Any, Callable, List, Set
from urllib.parse import urlparse
import attr, os

from typing import Optional
from pydantic import BaseModel
import csv
import logging

from trapper_client import Schemas
from trapper_client.APIClientBase import APIClientBase

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


#
# DeploymentsComponent
#

@attr.s
class LocationsComponent(TrapperAPIComponent):
    """
    Component for interacting with the Locations endpoint of the Trapper API.

    This component provides methods to retrieve location data, either individually
    or in bulk, and handles the mapping of API responses to Pydantic models.
    """

    def __attrs_post_init__(self):
        """
        Initialize the Locations component.

        This method sets the endpoint and schema used to query and validate
        the API responses for locations.
        """
        self._endpoint = "/geomap/api/locations/export/"
        self._schema = Schemas.TrapperLocationList

    def get_by_id(self, location_id: str) -> T:
        """
        Retrieve a single location by its ID.

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
            filter_fn=lambda dep: dep.id == location_id
        )

    def get_by_acronym(self, location_acro: str) -> T:
        """
        Retrieve locations matching a specific acronym.

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
            filter_fn=lambda dep: dep.locationID == location_acro
        )

    def get_by_research_project(self, research_project: str) -> T:
        """
        Retrieve locations associated with a specific research project.

        This method fetches all locations and applies a local filter to return
        only those linked to the specified research project.

        Parameters
        ----------
        research_project : str
            The ID or identifier of the research project to filter locations by.

        Returns
        -------
        T
            A list or Pydantic model containing the matching location(s).

        Examples
        --------
        # Fetch locations associated with research project "16.0"
        locations = locations_component.get_by_research_project("16.0")
        for loc in locations:
            print(loc.name)
        """
        return self.get_all(
            filter_fn=lambda dep: dep.researchProject == research_project
        )


#
# DeploymentsComponent
#

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


#
# ClassificationProjectsComponent
#

@attr.s
class ClassificationProjectsComponent(TrapperAPIComponent):
    def __attrs_post_init__(self):
        self._endpoint = "/media_classification/api/projects"
        self._schema = Schemas.TrapperClassificationProjectList

    def get_by_id(self, project_id: int) -> T:
        """
        Retrieve a single classification project by its unique ID.

        Parameters
        ----------
        project_id : str
            The unique identifier of the classification project.

        Returns
        -------
        Schemas.TrapperClassificationProjectList
            A Pydantic model representing the classification project(s).

        Examples
        --------
        classification_project = classificaction_project_component.get_by_id("123")
        print(classification_project.results[0].id)
        """
        return self.get_all(query={"pk": project_id})

    def get_by_acronym(self, project_acro: str) -> T:
        """
        Retrieve classification projects by acronym.

        Parameters
        ----------
        project_acro : str
            The acronym or name to filter classification projects.

        Returns
        -------
        T
            Filtered classification projects whose name matching the acronym.
        """
        return self.get_all(
            filter_fn=lambda dep: dep.name == project_acro
        )

    def get_by_collection(self, collection_id: str) -> T:
        """
        Retrieve classification projects associated with a specific collection.

        Parameters
        ----------
        collection_id : str
            The ID of the collection to filter classification projects.

        Returns
        -------
        Schemas.TrapperClassificationProjectList
            Classification projects associated with the specified collection.
        """
        cps = self.get_all()
        result = []
        for cp in cps.results:
            collections = CollectionsComponent(self._client).get_by_classification_project(int(cp.pk))
            found = any(c.collection_pk == collection_id for c in collections.results)
            if found:
                result.append(cp)

        pagination = cps.pagination
        pagination.count = len(result)

        return Schemas.TrapperClassificationProjectList(**{"pagination": pagination, "results": result})


#
# ResearchProjectsComponent
#

@attr.s
class ResearchProjectsComponent(TrapperAPIComponent):
    """
    Retrieve classification projects associated with a specific collection.

    Parameters
    ----------
    collection_id : str
        The ID of the collection to filter classification projects.

    Returns
    -------
    Schemas.TrapperClassificationProjectList
        Classification projects associated with the specified collection.
    """

    def __attrs_post_init__(self):
        """
        Initialize the component with research projects endpoint and schema.
        """
        self._endpoint = "/research/api/projects"
        self._schema = Schemas.TrapperResearchProjectList

    def get_by_id(self, project_id: int) -> T:
        """
        Retrieve research project by ID.

        Parameters
        ----------
        project_id : int
            The ID of the research project.

        Returns
        -------
        T
            The research project with the specified ID.
        """
        return self.get_all(query={"pk": project_id})

    def get_by_acronym(self, project_acro: str) -> T:
        """
        Retrieve research projects by acronym.
    
        Parameters
        ----------
        project_acro : str
            The acronym or name to filter research projects.
    
        Returns
        -------
        T
            Filtered research projects whose name matching the acronym.
        """

        return self.get_all(
            filter_fn=lambda dep: dep.name == project_acro
        )

    def get_by_collection(self, collection_id: int) -> T:
        """
        Retrieve research projects associated with a specific collection.

        Parameters
        ----------
        collection_id : int
            The ID of the collection to filter research projects.

        Returns
        -------
        Schemas.TrapperResearchProjectList
            Research projects associated with the specified collection.
        """
        rps = self.get_all()
        result = []
        for cp in rps.results:
            collections = CollectionsComponent(self._client).get_by_research_project(int(cp.pk))
            found = any(int(c.collection_pk) == int(collection_id) for c in collections.results)
            if found:
                result.append(cp)

        pagination = rps.pagination
        pagination.count = len(result)

        return Schemas.TrapperResearchProjectList(**{"pagination": pagination, "results": result})

    def get_by_owner(self, owner: str) -> T:
        """
        Retrieve research projects by owner.

        Parameters
        ----------
        owner : str
            The owner username to filter research projects.

        Returns
        -------
        T
            Research projects owned by the specified user.
        """
        return self.get_all(
            filter_fn=lambda dep: dep.owner == owner
        )

    def get_my(self, username="me") -> T:
        """
        Retrieve research projects associated with the current user.

        Parameters
        ----------
        username : str, optional
            The username to filter by. Defaults to "me" for current user.

        Returns
        -------
        T
            Research projects where the user is owner or has specific roles.
        """
        if username == "me":
            username = self._client.user_name
        roles = ["Admin", "Collaborator", "Expert"]

        return self.get_all(
            filter_fn=lambda proj: (
                    (username and proj.owner == username)
                    or (
                            username
                            and any(
                        role.username == username and any(r in roles for r in role.roles)
                        for role in proj.project_roles
                    )
                    )
            )
        )


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

    def get_all(self, *args, **kwargs):
        raise NotImplementedError(
            "ResourcesComponent does not support get_all(). Use get_by_collection(cp_id) instead."
        )

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


@attr.s
class MediaComponent(TrapperAPIComponent):
    """
    Component for interacting with Media endpoint.

    Provides methods to retrieve and download media files from classification projects.
    """

    def __attrs_post_init__(self):
        """
        Initialize the component with media endpoint and schema.
        """
        self._endpoint = "/media_classification/api/media/{cp}/"
        self._schema = Schemas.TrapperMediaList

    def _download_trapper_media_list(self, media_list: Schemas.TrapperMediaList, zip_filename_base: str = None) -> List[
        str]:
        """
        Download media files and organize them into ZIP files.

        Parameters
        ----------
        media_list : Schemas.TrapperMediaList
            List of media items to download.
        zip_filename_base : str, optional
            Base name for the ZIP files. Defaults to "trapper_media_export".

        Returns
        -------
        List[str]
            List of paths to the created ZIP files.
        """

        MAX_ZIP_SIZE = 2 * 1024 ** 3  # 2 GB
        import tempfile, requests, zipfile
        temp_dir = Path(tempfile.mkdtemp(prefix="trapper_client_"))

        if zip_filename_base is None:
            zip_filename_base = "trapper_media_export"

        zip_filename_base = os.path.join(temp_dir, zip_filename_base)

        zip_files = []
        zip_index = 1
        current_zip_size = 0
        zip_writer = None

        def start_new_zip():
            nonlocal zip_index, zip_writer, current_zip_size
            zip_name = f"{zip_filename_base}_{zip_index:03}.zip"
            zip_writer = zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED)
            zip_files.append(zip_name)
            current_zip_size = 0
            return zip_name

        # Iniciar el primer zip
        start_new_zip()

        for media in media_list.results:
            file_url = media.filePath
            file_name = f"{media.mediaID}:{media.fileName}"
            deployment_id = media.deploymentID
            mediatype = media.fileMediatype or "image/jpeg"
            file_ext = ".jpg" if mediatype == "image/jpeg" else ""
            zip_internal_path = os.path.join(deployment_id, file_name + file_ext)

            try:
                response = requests.get(str(file_url))
                response.raise_for_status()
                file_data = response.content
                file_size = len(file_data)

                if current_zip_size + file_size > MAX_ZIP_SIZE:
                    zip_writer.close()
                    zip_index += 1
                    start_new_zip()

                zip_writer.writestr(zip_internal_path, file_data)
                current_zip_size += file_size

            except Exception as e:
                print(f"❌ Error descargando {file_name}: {e}")

        if zip_writer:
            zip_writer.close()

        return temp_dir

    def get_all(self, *args, **kwargs):
        raise NotImplementedError(
            "MediaComponent does not support get_all(). Use get_by_classification_project(cp_id) instead."
        )

    def get_by_classification_project(self, cp_id: int, query: dict = None) -> T:
        """
        Retrieve media from a specific classification project.

        Parameters
        ----------
        cp_id : int
            The ID of the classification project (replaces {cp} in the endpoint).
        query : dict, optional
            Optional search/pagination parameters.

        Returns
        -------
        Schemas.TrapperMediaList
            Media items associated with the specified classification project.
        """

        endpoint = self._endpoint.format(cp=cp_id)
        res = self._client.get_all_pages(endpoint, query)
        return self._schema(**res)

    def get_by_classification_project_and_collection(self, cp_id: int, c_id:int, query: dict = None) -> T:
        """
        Retrieve media from a specific classification project and collection.

        Parameters
        ----------
        cp_id : int
            The ID of the classification project (replaces {cp} in the endpoint).
        c_id : int
            The ID of the collection to filter media by.
        query : dict, optional
            Optional search/pagination parameters.

        Returns
        -------
        Schemas.TrapperMediaList
            Media items associated with the specified classification project and collection.
        """
        resources: ResourcesComponent = ResourcesComponent(self._client)

        collection_resources = resources.get_by_collection(c_id)
        media_ids : Set[str] = { resource.pk for resource in collection_resources.results }

        endpoint = self._endpoint.format(cp=cp_id)
        res = Schemas.TrapperMediaList(**self._client.get_all_pages(endpoint, query))
        filtered = [entry for entry in res.results if entry.mediaID in media_ids]
        res.pagination.count = len(filtered)
        res.results = filtered

        return res


    def get_by_classification_project_only_animals(self, cp_id: int, query: dict = None) -> T:
        """
        Retrieve media containing only animal observations from a classification project.

        Parameters
        ----------
        cp_id : int
            The ID of the classification project.
        query : dict, optional
            Optional search/pagination parameters.

        Returns
        -------
        Schemas.TrapperMediaList
            Media items containing only animal observations.
        """

        # Obtenemos los mediaid de los media que solo tengan animales
        observations: ObservationsComponent = ObservationsComponent(self._client)
        o = observations.get_by_classification_project(cp_id, query)

        mediaid_groups = defaultdict(list)
        for entry in o.results:
            mediaid_groups[entry.mediaID].append(entry)

        filtered = []
        for mediaid, entries in mediaid_groups.items():
            if all(e.observationType == 'animal' for e in entries):
                filtered.extend(entries)

        # Obtenemos todos los medias del proyecto de clasificacion
        endpoint = self._endpoint.format(cp=cp_id)
        res = self._client.get_all_pages(endpoint, query)
        medias = self._schema(**res)

        # Obtener el conjunto de mediaIDs válidos del paso anterior
        valid_media_ids = {obs.mediaID for obs in filtered}

        # Filtrar las entradas multimedia que tienen esos mediaIDs
        filtered = [entry for entry in medias.results if entry.mediaID in valid_media_ids]

        pagination = medias.pagination
        pagination.count = len(valid_media_ids)

        return Schemas.TrapperMediaList(**{"pagination": pagination, "results": filtered})

    def download_by_classification_project(self, cp_id: int, query: dict = None, zip_filename_base: str = None):
        """
        Download all media from a classification project.

        Parameters
        ----------
        cp_id : int
            The ID of the classification project.
        query : dict, optional
            Optional search/pagination parameters.
        zip_filename_base : str, optional
            Base name for the ZIP files.

        Returns
        -------
        List[str]
            Paths to the created ZIP files.
        """
        results = self.get_by_classification_project(cp_id, query)
        zip_files = self._download_trapper_media_list(results, zip_filename_base)
        return zip_files

    def download_by_classification_project_and_collection(self, cp_id: int, c_id:int, query: dict = None, zip_filename_base: str = None):
        """
        Download all media from a specific classification project and collection.

        Parameters
        ----------
        cp_id : int
            The ID of the classification project.
        c_id : int
            The ID of the collection.
        query : dict, optional
            Optional search/pagination parameters.
        zip_filename_base : str, optional
            Base name for the ZIP files.

        Returns
        -------
        List[str]
            Paths to the created ZIP files.
        """


        results = self.get_by_classification_project_and_collection(cp_id, c_id, query)
        zip_files = self._download_trapper_media_list(results, zip_filename_base)
        return zip_files

    def download_by_classification_project_only_animals(self, cp_id: int, query: dict = None,
                                                        zip_filename_base: str = None):
        """
        Download media containing only animal observations from a classification project.

        Parameters
        ----------
        cp_id : int
            The ID of the classification project.
        query : dict, optional
            Optional search/pagination parameters.
        zip_filename_base : str, optional
            Base name for the ZIP files.

        Returns
        -------
        List[str]
            Paths to the created ZIP files.
        """

        results = self.get_by_classification_project_only_animals(cp_id, query)
        zip_files = self._download_trapper_media_list(results, zip_filename_base)
        return zip_files


@attr.s
class ObservationsComponent(TrapperAPIComponent):
    """
    Component for interacting with Observations endpoint.

    Provides methods to retrieve observation data from classification projects.
    """

    def __attrs_post_init__(self):
        """
        Initialize the component with observations endpoint and schema.
        """
        self._endpoint = "/media_classification/api/classifications/results/{cp}/"
        self._schema = Schemas.TrapperObservationList

    def get_all(self, *args, **kwargs):
        raise NotImplementedError(
            "ObservationsComponent does not support get_all(). Use get_by_classification_project(cp_id) instead."
        )

    def get_by_classification_project(self, cp_id: int, query: dict = None) -> T:
        """
        Retrieve observations from a specific classification project.

        Parameters
        ----------
        cp_id : int
            The ID of the classification project (replaces {cp} in the endpoint).
        query : dict, optional
            Optional search/pagination parameters.

        Returns
        -------
        Schemas.TrapperObservationList
            Observations from the specified classification project.
        """
        endpoint = self._endpoint.format(cp=cp_id)
        res = self._client.get_all_pages(endpoint, query)
        return self._schema(**res)

    def get_by_classification_project_and_collection(self, cp_id: int, c_id:int, query: dict = None) -> T:
        """
        Retrieve observations from a specific classification project and collection.

        Parameters
        ----------
        cp_id : int
            The ID of the classification project (replaces {cp} in the endpoint).
        c_id : int
            The ID of the collection to filter observations by.
        query : dict, optional
            Optional search/pagination parameters.

        Returns
        -------
        Schemas.TrapperObservationList
            Observations from the specified classification project and collection.
        """

        resources: ResourcesComponent = ResourcesComponent(self._client)

        collection_resources = resources.get_by_collection(c_id)
        media_ids : Set[str] = { resource.pk for resource in collection_resources.results }

        endpoint = self._endpoint.format(cp=cp_id)
        res = Schemas.TrapperObservationList(**self._client.get_all_pages(endpoint, query))
        filtered = [entry for entry in res.results if entry.mediaID in media_ids]
        res.pagination.count = len(filtered)
        res.results = filtered

        return res

#
# Main client class
#

def parse_url(url: str):
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"URL inválida: {url}")
    return url


@attr.s(auto_attribs=True)
class TrapperClient:
    """
    Main client for interacting with the Trapper API.

    This client wraps around multiple API components (locations, deployments, etc.)
    and manages authentication, requests, and schema validation.

    Attributes
    ----------
    access_token : str
        Authentication token for API access.
    base_url : str
        Base URL of the Trapper API server.
    user_name : str
        Username for authentication.
    user_password : str
        Password for authentication.
    raw : APIClientBase
        Raw API client instance.
    locations : LocationsComponent
        Component for location-related operations.
    deployments : DeploymentsComponent
        Component for deployment-related operations.
    classification_projects : ClassificationProjectsComponent
        Component for classification project operations.
    research_projects : ResearchProjectsComponent
        Component for research project operations.
    resources : ResourcesComponent
        Component for resource-related operations.
    media : MediaComponent
        Component for media-related operations.
    observations : ObservationsComponent
        Component for observation-related operations.
    collections : CollectionsComponent
        Component for collection-related operations.

    """
    access_token: str
    base_url: str = attr.ib(default="https://wildintel-trap.uhu.es", converter=parse_url)
    user_name: str = attr.ib(repr=False, default="me")
    user_password: str = attr.ib(repr=False, default="")

    raw: APIClientBase = attr.ib(init=False, repr=False)

    def __attrs_post_init__(self):
        self.raw: APIClientBase = APIClientBase(
            access_token=self.access_token,
            user_name=self.user_name,
            user_password=self.user_password,
            base_url=self.base_url,
        )
        self.locations: LocationsComponent = LocationsComponent(self.raw)
        self.deployments: DeploymentsComponent = DeploymentsComponent(self.raw)
        self.classification_projects: ClassificationProjectsComponent = ClassificationProjectsComponent(self.raw)
        self.research_projects: ResearchProjectsComponent = ResearchProjectsComponent(self.raw)
        self.resources: ResourcesComponent = ResourcesComponent(self.raw)
        self.media: MediaComponent = MediaComponent(self.raw)
        self.observations: ObservationsComponent = ObservationsComponent(self.raw)
        self.collections: CollectionsComponent = CollectionsComponent(self.raw)

    @classmethod
    def from_environment(cls) -> "TrapperClient":
        """
        Create a TrapperClient instance using environment variables.

        Returns
        -------
        TrapperClient
            A new TrapperClient instance configured from environment variables.

        Environment Variables
        ---------------------
        TRAPPER_ACCESS_TOKEN : str
            Authentication token for API access.
        TRAPPER_URL : str
            Base URL of the Trapper API server.
        TRAPPER_USER_NAME : str
            Username for authentication.
        TRAPPER_USER_PASSWORD : str
            Password for authentication.
        """
        env = os.environ
        return cls(
            access_token=env.get("TRAPPER_ACCESS_TOKEN", None),
            base_url=env.get("TRAPPER_URL", "https://wildintel-trap.uhu.es"),
            user_name=env.get("TRAPPER_USER_NAME", None),
            user_password=env.get("TRAPPER_USER_PASSWORD", None),
        )

    @staticmethod
    def export_list_to_csv(data_list: BaseModel, output_file: Optional[str] = None,
                           include_pagination: bool = False):
        """
        Export a Pydantic list object with pagination to CSV.

        Parameters
        ----------
        data_list : BaseModel
            Pydantic model containing 'pagination' and 'results' attributes.
        output_file : str, optional
            Optional path to a CSV file. Defaults to stdout.
        include_pagination : bool, optional
            If True, adds pagination fields to each row. Defaults to False.

        Returns
        -------
        str or None
            The output file path if output_file was provided, otherwise None.

        Raises
        ------
        ValueError
            If the provided object doesn't have 'results' and 'pagination' attributes.
        """

        if not hasattr(data_list, "results") or not hasattr(data_list, "pagination"):
            raise ValueError("The provided object must have 'results' and 'pagination' attributes.")
        if not hasattr(data_list, "results") or not hasattr(data_list, "pagination"):
            raise ValueError("The provided object must have 'results' and 'pagination' attributes.")

        results = data_list.results
        if not results:
            print("No data to export.")
            return

        # Base field names from the first result
        fieldnames = [
            field.alias if field.alias else name
            for name, field in type(results[0]).model_fields.items()
        ]

        # Add pagination fields if requested
        if include_pagination:
            pagination_fields = ["page", "page_size", "pages", "count"]
            fieldnames = pagination_fields + fieldnames

        output = open(output_file, "w", newline="", encoding="utf-8") if output_file else sys.stdout
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for item in results:
            row = item.model_dump(by_alias=True)
            if include_pagination:
                row = {**data_list.pagination.model_dump(), **row}
            writer.writerow(row)

        if output_file:
            output.close()

        return output_file
