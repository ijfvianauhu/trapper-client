from pathlib import Path
from typing import Dict, Any, Callable, TypeVar, Set

from pydantic import BaseModel

from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr

from trapper_client.components.CollectionsComponent import CollectionsComponent
from trapper_client.components.ResourcesComponent import ResourcesComponent
import logging
logger = logging.getLogger(__name__)

@attr.s
class ObservationsResultsComponent(TrapperAPIComponent):
    explicit_fields = [
        "pk",
        "project",
        "owner",
        "deployment",
#       "collection",
        "locations_map",
        "status",
        "status_ai", "rdate_from", "rdate_to",
        "rtime_from",
        "rtime_to",
        "ftype",
        "classified",
        "classified_ai",
        "bboxes",
        "species",
        "observation_type",
        "sex",
        "age"
        "pk",
    ]

    _endpoint = "/media_classification/api/classifications/results/{cp}"
    _schema = Schemas.TrapperClassificationResultsList
    _default_query = {"camtrapdp" : "True"}

    def set_camtrapdp_format(self):
        """
        Set the camtrapdp format for the endpoint.

        Parameters
        ----------
        camtrapdp : bool
            If True, set the endpoint to use camtrapdp format.
        """
        self._default_query["camtrapdp"] = "True"

    def unset_camtrapdp_format(self):
        """
        Set the camtrapdp format for the endpoint.

        Parameters
        ----------
        camtrapdp : bool
            If True, set the endpoint to use camtrapdp format.
        """
        self._default_query["camtrapdp"] = "false"

    def __attrs_post_init__(self):
        """
        Initialize the component with observations endpoint and schema.
        """

    def get_all(self, *args, **kwargs):
        raise NotImplementedError(
            "ObservationsResultsComponent does not support get_all(). Use get_by_*(cp_id) instead."
        )

    #def get(self, *args, **kwargs):
    #    raise NotImplementedError(
    #        "ObservationsResultsComponent does not support get_all(). Use get_by_*(cp_id) instead."
    #    )

    def get_by_collection(self, cp_id:int, c_id:int, query: dict = None) -> T:
        """
        Retrieve Observation Results from a specific classification project and collection.

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

        collections:CollectionsComponent = CollectionsComponent(self._client)
        results = collections.get_by_classification_project(cp_id)
        logger.info(results)

        collection_inter_id = [ r.pk for r in results.results if r.collection_pk == c_id ]

        if len(collection_inter_id) == 0:
            return Schemas.TrapperClassificationResultsList(**{"pagination": {"count":0, "next":None, "previous":None}, "results":[]})

        q = query.copy() if query else {}
        q["collection"] = ",".join(map(str, collection_inter_id))

        res = super().get_all(
                query = q,
                filter_fn = None,
                endpoint = self._endpoint.format(cp=cp_id),
        )

        return res

@attr.s
class ObservationsComponent(TrapperAPIComponent):
    """
    Component for interacting with Observations endpoint.

    Provides methods to retrieve observation data from classification projects.
    """

    explicit_fields = [
        "pk",  # int → Identificador único del registro (primary key).
        "project",  # int → ID del proyecto de clasificación (project__pk).
        "owner",  # bool → Si true, devuelve recursos propiedad o gestionados por el usuario.
        "deployment",  # int o list[int] → Filtra por uno o varios deployments (resource__deployment).
#        "collection",  # int o list[int] → Filtra por colecciones dentro del proyecto.
        "locations_map",  # dict / custom → Filtro geográfico según BaseLocationsMapFilter.
        "status",  # bool → Filtra clasificaciones activas/inactivas.
        "status_ai",  # bool → Filtra por estado de clasificación automática (IA).
        "rdate_from",  # str (YYYY-MM-DD) → Fecha mínima de captura (>=).
        "rdate_to",  # str (YYYY-MM-DD) → Fecha máxima de captura (<=).
        "rtime_from",  # str (HH:MM) → Hora mínima dentro del día.
        "rtime_to",  # str (HH:MM) → Hora máxima dentro del día.
        "ftype",  # str → Tipo de recurso (image, video, etc.).
        "classified",  # bool → True: tiene clasificaciones humanas; False: no tiene.
        "classified_ai",  # bool → True: tiene clasificaciones de IA; False: no tiene.
        "bboxes",  # bool → True: contiene bounding boxes (detecciones).
        "species",  # int o list[int] → Filtra por especie (dynamic_attrs__species).
        "observation_type",  # str → Tipo de observación (ObservationType.get_all_choices()).
        "sex",  # str → Sexo del animal (SpeciesSex.get_all_choices()).
        "age",  # str → Edad del animal (SpeciesAge.get_all_choices()).
    ]

    _endpoint = "/media_classification/api/classifications"
    _schema = Schemas.TrapperClassificationList
    results = None # ResultsObservationsComponent

    def __attrs_post_init__(self):
        """
        Initialize the component with observations endpoint and schema.
        """
        self.results = ObservationsResultsComponent(self._client)

    def get_all_by_collection(self, cp_id:int, c_id:int, query: dict = None) -> T:
        collections = CollectionsComponent(self._client).get_by_classification_project(int(cp_id), query)
        collection = [col for col in collections.results if str(col.collection_pk) == str(c_id)]

        query = query.copy() if query else {}
        query["collection"] = collection[0].pk
        query["project"] = cp_id
        logger.debug(collection)

        return self.get_all(query, None, f"/media_classification/api/classifications/results/{cp_id}/")

    def get_by_collection(self, cp_id:int, c_id:int, query: dict = None) -> T:
        logger.debug(f"Getting internal id for collection {c_id}")
        collections = CollectionsComponent(self._client).get_by_classification_project(int(cp_id), query)
        collection = [col for col in collections.results if str(col.collection_pk) == str(c_id)]

        if len(collection) == 0:
            return Schemas.TrapperMediaList(**{"pagination": {"count":0, "next":None, "previous":None}, "results":[]})

        query = query.copy() if query else {}
        query["collection"] = collection[0].pk
        query["project"] = cp_id
        logger.debug(f"Internal id {collection}")

        return self.get(query)


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

    def get_all_by_classification_project_and_collection(self, cp_id: int, c_id:int, query: dict = None) -> T:
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
        collections = CollectionsComponent(self._client).get_by_classification_project(int(cp_id), query)
        collection = [col for col in collections.results if str(col.collection_pk) == str(c_id)]

        endpoint = f"/media_classification/api/classifications/results/{cp_id}/"

        query = query.copy() if query else {}
        query["collection"] = collection[0].pk

        return self.get_all(query, None, endpoint)


# ###########################################################################################
# TABLE
# ###########################################################################################

class MediaTableObservationsResultsComponent(ObservationsResultsComponent):
    def __attrs_post_init__(self):
        """
        Initialize the component with observations endpoint and schema.
        """
        self._endpoint = "/media_classification/api/classifications/media_table/{cp}"
        self._schema = Schemas.TrapperClassificationList


# ###########################################################################################
# AGGREGATED
# ###########################################################################################

class AggObservationsResultsComponent(ObservationsResultsComponent):
    def __attrs_post_init__(self):
        """
        Initialize the component with observations endpoint and schema.
        """
        self._endpoint = "/media_classification/api/classifications/results_agg/{cp}"
        self._schema = Schemas.TrapperClassificationList

# ###########################################################################################
# AI
# ###########################################################################################
@attr.s
class AIObservationsResultsComponent(TrapperAPIComponent):

    explicit_fields = [
        "pk"
        "project",
        "deployment",
        "collection",
        "ftype",
        "species",
        "observation_type",
        "bboxes",
        "approved",
        "confidence",
        "ai_provider",
        #(+ custom_attrs del clasificator)
    ]

    _endpoint = "/media_classification/api/ai-classifications/results/{cp}"
    _schema : BaseModel = Schemas.TrapperClassificationResultsList
    _default_query = {"camtrapdp" : "True"}

    def set_camtrapdp_format(self):
        """
        Set the camtrapdp format for the endpoint.

        Parameters
        ----------
        camtrapdp : bool
            If True, set the endpoint to use camtrapdp format.
        """
        self._default_query["camtrapdp"] = "True"

    def unset_camtrapdp_format(self):
        """
        Set the camtrapdp format for the endpoint.

        Parameters
        ----------
        camtrapdp : bool
            If True, set the endpoint to use camtrapdp format.
        """
        self._default_query["camtrapdp"] = "false"

    def __init_subclass__(cls, **kwargs):
        """
        Dynamically generate getter methods for each explicit field when the subclass is created.
        """
        super().__init_subclass__(**kwargs)

    def __attrs_post_init__(self):
        """
        Initialize the component with observations endpoint and schema.
        """
        pass

    def get_all(
            self,
            cp_id:int,
            query: Dict[str, Any] = None,
            filter_fn: Callable[[T], bool] = None,
            endpoint: str = None,
            schema: T = None
    ) -> T:
        logger.info(f"Getting all AI Observation Results for classification project {cp_id} with query {query}")
        return super().get_all(query, filter_fn, endpoint= self._endpoint.format(cp=cp_id), schema= self._schema)

    def get_by_collection(self, cp_id:int, c_id:int, query: dict = None) -> T:
        """
        Retrieve Observation Results from a specific classification project and collection.

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

        collections:CollectionsComponent = CollectionsComponent(self._client)
        results = collections.get_by_classification_project(cp_id)
        logger.info(results)

        collection_inter_id = [ r.pk for r in results.results if r.collection_pk == c_id ]

        if len(collection_inter_id) == 0:
            # No hay colecciones asociadas al proyecto de clasificacion
            return Schemas.TrapperMediaList(**{"pagination": {"count":0, "next":None, "previous":None}, "results":[]})

        q = query.copy() if query else {}
        q["collection"] = ",".join(map(str, collection_inter_id))

        res = super().get_all(
                query = q,
                filter_fn = None,
                endpoint = self._endpoint.format(cp=cp_id),
        )

        return res


@attr.s
class AIObservationsComponent(TrapperAPIComponent):

    explicit_fields = [
        "pk"
        "project",
        "deployment",
#        "collection",
        "ftype",
        "species",
        "observation_type",
        "bboxes",
        "approved",
        "confidence",
        "ai_provider",
        #(+ custom_attrs del clasificator)
    ]

    _endpoint = "/media_classification/api/ai-classifications"
    _schema = Schemas.TrapperClassificationList
    results = None

    def __init_subclass__(cls, **kwargs):
        """
        Dynamically generate getter methods for each explicit field when the subclass is created.
        """
        super().__init_subclass__(**kwargs)

    def __attrs_post_init__(self):
        """
        Initialize the component with observations endpoint and schema.
        """
        self.results = AIObservationsResultsComponent(self._client)

    def get_by_collection(self, cp_id:int, c_id:int, query: dict = None) -> T:
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

        collections:CollectionsComponent = CollectionsComponent(self._client)
        results = collections.get_by_classification_project(cp_id)
        logger.info(results)

        collection_inter_id = [ r.pk for r in results.results if r.collection_pk == c_id ]

        if len(collection_inter_id) == 0:
            # No hay colecciones asociadas al proyecto de clasificacion
            return Schemas.TrapperMediaList(**{"pagination": {"count":0, "next":None, "previous":None}, "results":[]})

        q = query.copy() if query else {}
        q["collection"] = ",".join(map(str, collection_inter_id))
        q["project"] = cp_id

        res = super().get_all(
                query = q,
                filter_fn = None,
                endpoint = self._endpoint,
        )

        return res


#
@attr.s
class UserObservationsComponent(TrapperAPIComponent):

    explicit_fields = [
        "pk",
        "project",
        "user",
        "owner",
        "deployment",
#        "collection",
        "species",
        "ftype",
        "approved",
        "bboxes",
        "feedback",
        "observation_type",
        "locations_map",
        "rdate_from",
        "rdate_to",
        "rtime_from",
        "rtime_to"
    ]

    _endpoint = "media_classification/api/user-classifications"
    _schema = Schemas.TrapperClassificationList

    def get_by_collection(self, cp_id:int, c_id:int, query: dict = None) -> T:
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

        collections:CollectionsComponent = CollectionsComponent(self._client)
        results = collections.get_by_classification_project(cp_id)
        logger.info(results)

        collection_inter_id = [ r.pk for r in results.results if r.collection_pk == c_id ]

        if len(collection_inter_id) == 0:
            # No hay colecciones asociadas al proyecto de clasificacion
            return Schemas.TrapperMediaList(**{"pagination": {"count":0, "next":None, "previous":None}, "results":[]})

        q = query.copy() if query else {}
        q["collection"] = ",".join(map(str, collection_inter_id))
        q["project"] = cp_id

        res = super().get_all(
                query = q,
                filter_fn = None,
                endpoint = self._endpoint,
        )

        return res

