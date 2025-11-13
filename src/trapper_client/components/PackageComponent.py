import os
from typing import Dict, Any, Callable, TypeVar, List, Set

import requests

from trapper_client import Schemas
from trapper_client.TrapperAPIComponent import TrapperAPIComponent, T
import attr

import logging

logger = logging.getLogger(__name__)

@attr.s
class PackagesComponent(TrapperAPIComponent):
    """
    Component for interacting with Media endpoint.

    Provides methods to retrieve and download media files from classification projects.
    """
    _endpoint = "/media_classification/api/package/{cp}/"
    _schema = Schemas.TrapperMediaList

    explicit_fields = [
    ]

    package_generation_params = [
        "clear_cache",  # bool: Forzar regeneración del paquete aunque ya exista en caché
        "release",  # bool: Indica si se marca el paquete como release oficial
        "get_released",  # bool: Recuperar el último paquete marcado como release
        "export_format",  # str: Formato de exportación, ejemplo "camtrapdp"
        "export_filetype",  # str: Tipo de archivo, ejemplo "csv.gz"
        "approved_only",  # bool: Incluir solo clasificaciones aprobadas
        "exclude_blank",  # bool: Excluir registros sin clasificaciones
        "all_deployments",  # bool: Incluir todos los deployments del proyecto
        "filter_deployments",  # str: Filtrar deployments por substring en deployment_id
        "include_events",  # bool: Incluir eventos en el paquete
        "events_count_var",  # str: Variable de conteo de eventos, ejemplo "count"
        "trapper_url_token",  # bool: Incluir token en URLs para acceder a recursos privados
        "private_human",  # bool: Incluir datos privados de humanos
        "private_vehicle",  # bool: Incluir datos privados de vehículos
        "private_species",  # list: Lista de especies privadas a incluir
    ]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)


    def generate(self, cp: int, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Genera un paquete para el proyecto de clasificación especificado.

        :param cp: ID del proyecto de clasificación.
        :param params: Diccionario de parámetros para la generación del paquete.
        :return: Diccionario con información sobre el paquete generado.
        """
        if params is None:
            params = {}

        # Filtrar solo los parámetros válidos
        valid_params = {k: v for k, v in params.items() if k in self.package_generation_params}

        logger.info(valid_params)

        endpoint = self._endpoint.format(cp=cp)
        response = self._client.make_request(endpoint=endpoint, method="GET",query=valid_params,
                                             body=None,raise_on_error=True, only_json=True)
        data = response.json()

        errors = data['results'][0]['data']['errors']
        package = data['results'][0]['data']['package']

        return {"errors": errors, "package": package}

    def download(self, package_url: str, destination_folder: str) -> str:
        """
        Descarga el paquete desde la URL proporcionada y lo guarda en la carpeta de destino.

        :param package_url: URL del paquete a descargar.
        :param destination_folder: Carpeta donde se guardará el paquete descargado.
        :return: Ruta completa del archivo descargado.
        """
        resp = requests.get(package_url, stream=True, timeout=60)
        resp.raise_for_status()

        # Intentar extraer filename desde Content-Disposition
        filename = None
        cd = resp.headers.get("content-disposition")
        if cd:
            _,filename = cd.split(";",1)
            _,filename  = filename.split("=",maxsplit=1)

            logger.info(filename)

        # Fallback a la última parte de la URL
        if not filename:
            filename = package_url.rstrip("/").split("/")[-1] or "downloaded_package"

        # Asegurar que la carpeta destino existe
        os.makedirs(destination_folder, exist_ok=True)
        destination_path = os.path.join(destination_folder, filename)

        # Guardar el contenido por chunks
        with open(destination_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return destination_path
        return destination_path
## Fuerzo que se cree los métodos dinámicos,
#   MediaComponent.__init_subclass__()