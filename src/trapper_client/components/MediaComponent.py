import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, Callable, TypeVar, List, Set

from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr

from trapper_client.components.ObservationsComponent import ObservationsComponent
from trapper_client.components.ResourcesComponent import ResourcesComponent


@attr.s
class MediaComponent(TrapperAPIComponent):
    """
    Component for interacting with Media endpoint.

    Provides methods to retrieve and download media files from classification projects.
    """

    explicit_fields = [
        # Parámetros principales
        "project",
        "owner",
        "deployment",
        "collection",
        "locations_map",
        "status",
        "status_ai",

        # Filtros de fecha y hora
        "rdate_from",
        "rdate_to",
        "rtime_from",
        "rtime_to",

        # Tipo de archivo
        "ftype",

        # Estado de clasificación
        "classified",
        "classified_ai",
        "bboxes",

        # Atributos estándar
        "species",
        "observation_type",
        "sex",
        "age",

        # Atributos personalizados (definidos en cada proyecto)
        # se agregan dinámicamente, por ejemplo:
        # "weather", "temperature", "habitat", etc.
    ]

    def __attrs_post_init__(self):
        """
        Initialize the component with media endpoint and schema.
        """
        self._endpoint = "/media_classification/api/media/{cp}/"
        self._schema = Schemas.TrapperMediaList

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        for field in cls.explicit_fields:

            def make_getter(f=field, all_results=False):  # ← aquí se fija el valor
                prefix = "get_all_by_" if all_results else "get_by_"
                method_name = f"{prefix}{f}"

                def getter(self, cp_id, value, query=None, filter_fn=None, endpoint=None):
                    query = query or {}
                    if isinstance(value, list):
                        value = ",".join(map(str, value))
                    query[f] = value
                    endpoint = endpoint or self._endpoint.format(cp=cp_id)
                    if all_results:
                        return self.get_all(query, filter_fn=filter_fn, endpoint=endpoint)
                    return self.get(query, filter_fn=filter_fn, endpoint=endpoint)

                getter.__name__ = method_name
                getter.__doc__ = f"""
    Auto-generated method for querying Media by field '{f}' within a classification project.

    Parameters
    ----------
    cp_id : int
        ID of the classification project.
    value : Any
        Value to filter by for field '{f}'.
    query : dict, optional
        Additional query parameters.
    filter_fn : callable, optional
        Local filter function.
    endpoint : str, optional
        Endpoint override.

    Returns
    -------
    T
        Filtered results from the API.
    """
                return getter

            setattr(cls, f"get_by_{field}", make_getter(field))
            setattr(cls, f"get_all_by_{field}", make_getter(field, all_results=True))

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

## Fuerzo que se cree los métodos dinámicos,
MediaComponent.__init_subclass__()