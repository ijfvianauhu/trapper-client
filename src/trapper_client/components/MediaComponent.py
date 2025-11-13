import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, Callable, TypeVar, List, Set

from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr

from trapper_client.components.CollectionsComponent import CollectionsComponent
from trapper_client.components.ObservationsComponent import ObservationsComponent
from trapper_client.components.ResourcesComponent import ResourcesComponent
import logging

logger = logging.getLogger(__name__)

@attr.s
class MediaComponent(TrapperAPIComponent):
    """
    Component for interacting with Media endpoint.

    Provides methods to retrieve and download media files from classification projects.
    """
    _endpoint = "/media_classification/api/media/{cp}/"
    _schema = Schemas.TrapperMediaList

    explicit_fields = [
        "project",
        "owner",
        "deployment",
#        "collection", --> overridden in self. get_by_collection (resol collection_id through CollectionsComponent)
        "locations_map",
        "status",
        "status_ai",
        "rdate_from",
        "rdate_to",
        "rtime_from",
        "rtime_to",
        "ftype",
        "classified",
        "classified_ai",
        "bboxes",
        # Dynamic attributes related to observations
        "species",
        "observation_type",
        "sex",
        "age",
        # Atributos personalizados (definidos en cada proyecto)
        # se agregan dinámicamente, por ejemplo:
        # "weather", "temperature", "habitat", etc.
    ]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

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

    def get_by_collection(self, cp_id: int, c_id:int, query: dict = None) -> T:
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

        res = super().get_all(
                query = q,
                filter_fn = None,
                endpoint = self._endpoint.format(cp=cp_id),
        )

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

## Fuerzo que se cree los métodos dinámicos,
#   MediaComponent.__init_subclass__()