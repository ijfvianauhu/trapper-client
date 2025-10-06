from typing import TypeVar, Type, Dict, Any, Callable
from urllib.parse import urlparse
import attr, os

from trapper_client import Schemas
from trapper_client.APIClientBase import APIClientBase
import trapper_client.Schemas

T = TypeVar("T")

@attr.s
class TrapperAPIComponent:
    _client: APIClientBase = attr.ib(repr=False)
    _endpoint: str = attr.ib(init=False)
    _schema: Type[T] = attr.ib(init=False)

    def get_all(self, query: Dict[str, Any] = None, filter_fn: Callable[[T], bool] = None) -> T:
        """
        Recupera todos los resultados del endpoint.
        - query: diccionario con parámetros de búsqueda
        - filter_fn: función opcional para filtrar los resultados (lambda u objeto callable)
        """
        import json
        res = self._client.get_all_pages(self._endpoint, query)
        #print(json.dumps(res, indent=4, sort_keys=True))

        parsed = self._schema(**res)

        if filter_fn:
            parsed.results = [r for r in parsed.results if filter_fn(r)]

        return parsed


#
# DeploymentsComponent
#

@attr.s
class LocationsComponent(TrapperAPIComponent):
    def __attrs_post_init__(self):
        self._endpoint = "/geomap/api/locations/export/"
        self._schema = Schemas.TrapperLocationList

    def get_by_id(self, location_id: str) -> T:
        return self.get_all(
            filter_fn=lambda dep: dep.id == location_id
        )

    def get_by_acronym(self, location_acro: str) -> T:
        return self.get_all(
            filter_fn=lambda dep: dep.locationID == location_acro
        )

    def get_by_research_project(self, research_project: str) -> T:
        return self.get_all(
            filter_fn=lambda dep: dep.researchProject == research_project
        )
#
# DeploymentsComponent
#

@attr.s
class DeploymentsComponent(TrapperAPIComponent):
    def __attrs_post_init__(self):
        self._endpoint = "/geomap/api/deployments/export/"
        self._schema = Schemas.TrapperDeploymentList

    def get_by_id(self, deployment_id: str) -> T:
        return self.get_all(
            filter_fn=lambda dep: dep.id == deployment_id
        )

    def get_by_acronym(self, deployment_acro: str) -> T:
        return self.get_all(
            filter_fn=lambda dep: dep.deploymentID == deployment_acro
        )

    def get_by_location(self, location_id: str) -> T:
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
        return self.get_all(query={"pk": project_id})

    def get_by_acronym(self, project_acro: str) -> T:
        return self.get_all(
            filter_fn=lambda dep: dep.name == project_acro
        )

    def get_by_collection(self, collection_id: str) -> T:
        cps = self.get_all()
        result = []
        for cp in cps["results"]:
            collections = CollectionsComponent(self._client).get_by_classification_project(int(cp["pk"]))
            found = any(c.collection_pk == collection_id for c in collections.results)
            if found:
                result.append(cp)

        pagination = cps["pagination"]
        pagination["count"] = len(result)

        data = {"pagination": pagination, "results": result}

        filtered_data = data

        return filtered_data

#
# ResearchProjectsComponent
#

@attr.s
class ResearchProjectsComponent(TrapperAPIComponent):
    def __attrs_post_init__(self):
        self._endpoint = "/research/api/projects"
        self._schema = Schemas.TrapperResearchProjectList

    def get_by_id(self, project_id: int) -> T:
        return self.get_all(query={"pk": project_id})

    def get_by_acronym(self, project_acro: str) -> T:
        return self.get_all(
            filter_fn=lambda dep: dep.name == project_acro
        )

    def get_by_collection(self, collection_id: int) -> T:
        rps = self.get_all()
        result = []
        for cp in rps["results"]:
            collections = CollectionsComponent(self._client).get_by_research_project(int(cp["pk"]))
            found = any(c.collection_pk == collection_id for c in collections.results)
            if found:
                result.append(cp)

        pagination = rps["pagination"]
        pagination["count"] = len(result)

        data = {"pagination": pagination, "results": result}

        filtered_data = data
        return data

    def get_by_owner(self, owner: str) -> T:
        return self.get_all(
            filter_fn=lambda dep: dep.owner == owner
        )

    def get_my(self, username = "me") -> T:
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
    def __attrs_post_init__(self):
        self._endpoint = "/storage/api/collections"
        self._schema = Schemas.TrapperCollectionList

    def get_by_id(self, project_id: int) -> T:
        return self.get_all(query={"pk": project_id})

    def get_by_acronym(self, project_acro: str) -> T:
        return self.get_all(
            filter_fn=lambda dep: dep.name == project_acro
        )

    def get_by_research_project(self, project_id: int) -> T:
        endpoint = f"/research/api/project/{project_id}/collections"
        res =  self._client.get_all_pages(endpoint)
        return self._schema(**res)

    def get_by_classification_project(self, project_id: int) -> T:
        endpoint = f"/media_classification/api/project/{project_id}/collections"
        res = self._client.get_all_pages(endpoint)
        return self._schema(**res)

@attr.s
class ResourcesComponent(TrapperAPIComponent):
    def __attrs_post_init__(self):
        self._endpoint = "/storage/api/resources/collection/{pk}"
        self._schema = Schemas.TrapperResourceList

    def get_all(self, *args, **kwargs):
        raise NotImplementedError(
            "ResourcesComponent does not support get_all(). Use get_by_collection(cp_id) instead."
        )

    def get_by_collection(self, cp_id: int, query: dict = None) -> T:
        """
        Recupera las observaciones de un classification project específico.

        :param cp_id: ID del classification project (sustituye {cp} en el endpoint).
        :param query: parámetros opcionales de búsqueda/paginación.
        """
        endpoint = self._endpoint.format(pk=cp_id)
        res = self._client.get_all_pages(endpoint, query)
        return self._schema(**res)

    def get_by_location(self, cp_id: int, query: dict = None) -> T:
        """
        Recupera las observaciones de un classification project específico.

        :param cp_id: ID del classification project (sustituye {cp} en el endpoint).
        :param query: parámetros opcionales de búsqueda/paginación.
        """
        endpoint = f"/storage/api/resources/location/{cp_id}"
        res = self._client.get_all_pages(endpoint, query)

        return self._schema(**res)

@attr.s
class MediaComponent(TrapperAPIComponent):
    def __attrs_post_init__(self):
        self._endpoint = "/media_classification/api/media/{cp}/"
        self._schema = Schemas.TrapperMediaList

    def get_all(self, *args, **kwargs):
        raise NotImplementedError(
            "MediaComponent does not support get_all(). Use get_by_classification_project(cp_id) instead."
        )

    def get_by_classification_project(self, cp_id: int, query: dict = None) -> T:
        """
        Recupera las observaciones de un classification project específico.

        :param cp_id: ID del classification project (sustituye {cp} en el endpoint).
        :param query: parámetros opcionales de búsqueda/paginación.
        """
        endpoint = self._endpoint.format(cp=cp_id)
        res = self._client.get_all_pages(endpoint, query)
        return self._schema(**res)

@attr.s
class ObservationsComponent(TrapperAPIComponent):
    def __attrs_post_init__(self):
        self._endpoint = "/media_classification/api/classifications/results/{cp}/"
        self._schema = Schemas.TrapperObservationList

    def get_all(self, *args, **kwargs):
        raise NotImplementedError(
            "ObservationsComponent does not support get_all(). Use get_by_classification_project(cp_id) instead."
        )

    def get_by_classification_project(self, cp_id: int, query: dict = None) -> T:
        """
        Recupera las observaciones de un classification project específico.

        :param cp_id: ID del classification project (sustituye {cp} en el endpoint).
        :param query: parámetros opcionales de búsqueda/paginación.
        """
        endpoint = self._endpoint.format(cp=cp_id)
        res = self._client.get_all_pages(endpoint, query)
        return self._schema(**res)
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
    access_token: str
    base_url: str = attr.ib(default="https://wildintel-trap.uhu.es", converter=parse_url)
    user_name: str = attr.ib(repr=False, default="me")
    user_password: str = attr.ib(repr=False, default="")

    raw: APIClientBase = attr.ib(init=False, repr=False)
    #locations: LocationsComponent = attr.ib(init=False, repr=False)

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
        env = os.environ
        return cls(
            access_token=env.get("TRAPPER_ACCESS_TOKEN", None),
            base_url=env.get("TRAPPER_URL", "https://wildintel-trap.uhu.es"),
            user_name=env.get("TRAPPER_USER_NAME", None),
            user_password=env.get("TRAPPER_USER_PASSWORD", None),
        )

