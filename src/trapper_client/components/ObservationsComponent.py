from pathlib import Path
from typing import Dict, Any, Callable, TypeVar, Set

from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr

from trapper_client.components.ResourcesComponent import ResourcesComponent


@attr.s
class ObservationsComponent(TrapperAPIComponent):
    """
    Component for interacting with Observations endpoint.

    Provides methods to retrieve observation data from classification projects.

    Filtros disponibles en la querystring

    .. note::
    In general, the query string supports the following parameters:

    | Parámetro            | Tipo / Valores esperados                                 | Campo filtrado                           | Descripción                                                                      |
| -------------------- | -------------------------------------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------- |
| **project**          | `int`                                                    | `project__pk`                            | Filtra por el ID del proyecto de clasificación.                                  |
| **owner**            | `bool` (`true`/`false`)                                  | `resource__owner` / `resource__managers` | Si es `true`, devuelve solo recursos propiedad o gestionados por el usuario.     |
| **deployment**       | `int` o lista                                            | `resource__deployment`                   | Filtra por uno o varios *deployments*.                                           |
| **collection**       | `int` o lista                                            | `collection`                             | Filtra por colecciones dentro del proyecto.                                      |
| **locations_map**    | depende de `BaseLocationsMapFilter`                      | `resource__deployment__location`         | Filtra según ubicación geográfica.                                               |
| **status**           | `bool`                                                   | `status`                                 | Filtra clasificaciones con estado activo/inactivo (según tu modelo).             |
| **status_ai**        | `bool`                                                   | `status_ai`                              | Filtra por el estado de clasificación automática (IA).                           |
| **rdate_from**       | `YYYY-MM-DD`                                             | `resource__date_recorded__date__gte`     | Fecha mínima de captura.                                                         |
| **rdate_to**         | `YYYY-MM-DD`                                             | `resource__date_recorded__date__lte`     | Fecha máxima de captura.                                                         |
| **rtime_from**       | `HH:MM`                                                  | `resource__date_recorded__gte`           | Hora mínima (en el día).                                                         |
| **rtime_to**         | `HH:MM`                                                  | `resource__date_recorded__lte`           | Hora máxima (en el día).                                                         |
| **ftype**            | valores definidos en `ResourceType.get_all_choices()`    | `resource__resource_type`                | Tipo de recurso (p. ej. `image`, `video`, etc.).                                 |
| **classified**       | `true` / `false`                                         | Método `get_classified`                  | `true` → clasificaciones con usuarios; `false` → sin clasificaciones de usuario. |
| **classified_ai**    | `true` / `false`                                         | Método `get_classified_ai`               | `true` → tiene clasificación IA; `false` → no tiene.                             |
| **bboxes**           | `true` / `false`                                         | Método `has_bboxes`                      | `true` → contiene bounding boxes.                                                |
| **species**          | `int` o lista de IDs                                     | `dynamic_attrs__species`                 | Filtra por especie.                                                              |
| **observation_type** | valores definidos en `ObservationType.get_all_choices()` | `dynamic_attrs__observation_type`        | Tipo de observación (según tu modelo).                                           |
| **sex**              | valores definidos en `SpeciesSex.get_all_choices()`      | `dynamic_attrs__sex`                     | Sexo del animal observado.                                                       |
| **age**              | valores definidos en `SpeciesAge.get_all_choices()`      | `dynamic_attrs__age`                     | Edad del animal observado.                                                       |



    """

    def __attrs_post_init__(self):
        """
        Initialize the component with observations endpoint and schema.
        """
        self._endpoint = "/media_classification/api/classifications"
        self._schema = Schemas.TrapperClassificationList

    def get_all_user_classifications(self, query: Dict[str, Any] = None, filter_fn: Callable[[T], bool] = None) -> T:
        return self.get_all(query, filter_fn, "/media_classification/api/user-classifications")

    def get_user_classifications(self, query: Dict[str, Any] = None, filter_fn: Callable[[T], bool] = None) -> T:
        return self.get(query, filter_fn, "/media_classification/api/user-classifications")

    def get_all_ai_classifications(self, query: Dict[str, Any] = None, filter_fn: Callable[[T], bool] = None) -> T:
        return self.get_all(query, filter_fn, "/media_classification/api/ai-classifications")

    def get_ai_classifications(self, query: Dict[str, Any] = None, filter_fn: Callable[[T], bool] = None) -> T:
        return self.get(query, filter_fn, "/media_classification/api/ai-classifications")

    #ObservationsSerializer
    def get_all_by_classification_project(self, cp_id: int, query: Dict[str, Any] = None, camtrapdp:bool=False,
                                          filter_fn: Callable[[T], bool] = None) -> T:
        query = query.copy() if query else {}
        if camtrapdp:
            query["camtrapdp"] = "True"
        else:
            query["camtrapdp"] = "False"

        return self.get_all(query, filter_fn, f"/media_classification/api/classifications/results/{cp_id}/")

    def get_by_classification_project(self, cp_id: int, query: Dict[str, Any] = None, camtrapdp:bool=False,
                                      filter_fn: Callable[[T], bool] = None) -> T:
        query = query.copy() if query else {}
        if camtrapdp:
            query["camtrapdp"] = "True"
        else:
            query["camtrapdp"] = "False"

        return self.get(query, filter_fn, f"/media_classification/api/classifications/results/{cp_id}/")

    def get_all_ai_classifications_by_classification_project(self, cp_id: int, query: Dict[str, Any] = None,
                                        camtrapdp:bool=False,filter_fn: Callable[[T], bool] = None) -> T:
        query = query.copy() if query else {}
        if camtrapdp:
            query["camtrapdp"] = "True"
        else:
            query["camtrapdp"] = "False"

        return self.get_all(query, filter_fn, f"/media_classification/api/ai-classifications/results/{cp_id}/")

    def get_ai_classifications_by_classification_project(self, cp_id: int, query: Dict[str, Any] = None,
                                        camtrapdp:bool=False,filter_fn: Callable[[T], bool] = None) -> T:
        query = query.copy() if query else {}
        if camtrapdp:
            query["camtrapdp"] = "True"
        else:
            query["camtrapdp"] = "False"

        return self.get(query, filter_fn, f"/media_classification/api/ai-classifications/results/{cp_id}/")


    def get_all_aggregated_classifications_by_classification_project(self, cp_id: int, query: Dict[str, Any] = None,
                                        camtrapdp:bool=False,filter_fn: Callable[[T], bool] = None) -> T:
        query = query.copy() if query else {}
        if camtrapdp:
            query["camtrapdp"] = "True"
        else:
            query["camtrapdp"] = "False"

        return self.get_all(query, filter_fn, f"/media_classification/api/classifications/results/agg/{cp_id}/")

    def get_aggregated_classifications_by_classification_project(self, cp_id: int, query: Dict[str, Any] = None,
                                        camtrapdp:bool=False,filter_fn: Callable[[T], bool] = None) -> T:
        query = query.copy() if query else {}
        if camtrapdp:
            query["camtrapdp"] = "True"
        else:
            query["camtrapdp"] = "False"

        return self.get(query, filter_fn, f"/media_classification/api/classifications/results/agg/{cp_id}/")


    def _get_by_classification_project_and_collection(self, cp_id: int, c_id:int, query: dict = None) -> T:
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

    # api/classifications_map ClassificationMapViewSet