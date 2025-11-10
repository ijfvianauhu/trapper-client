import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperMedia

#
# pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

# Función común de validación de deployments
def _validate_objects(deployments, expected_type=TrapperMedia):
    """Common validation for deployments responses."""
    assert hasattr(deployments, "results")
    assert hasattr(deployments, "pagination")

    if deployments.results:  # solo si hay resultados
        assert isinstance(deployments.results[0], expected_type)

# Funciones de validación específicas
def validate_project(results, expected):
    pass

def validate_resource_type(results, expected):
    assert all(d.resource_type == expected for d in results)

def validate_name(results, expected):
    assert all(d.name == expected for d in results)

def validate_status(results, expected):
    pass

def validate_rdata_from(results, expected):
    from datetime import datetime
    expected_date = datetime.fromisoformat(expected)
    assert all(d.date_recorded >= expected_date for d in results)

# Diccionario de validaciones por filtro
VALIDATIONS = {
    "project": validate_project,
    "name": validate_name,
    "status": validate_status,
    "rdate_from": validate_rdata_from
}

#explicit_fields = [
#    "rdate_from",  # BaseDateFilter sobre date_recorded__date (gte)
#    "rdate_to",  # BaseDateFilter sobre date_recorded__date (lte)
#    "udate_from",  # BaseDateFilter sobre date_uploaded__date (gte)
#    "udate_to",  # BaseDateFilter sobre date_uploaded__date (lte)
#    "rtime_from",  # BaseTimeFilter sobre date_recorded (gte)
#    "rtime_to",  # BaseTimeFilter sobre date_recorded (lte)
#    "owner",  # OwnResourceBooleanFilter
#    "locations_map",  # BaseLocationsMapFilter sobre deployment__location
#    "collections",  # MultipleChoiceFilter
#    "deployments",  # CharFilter, método get_deployments
#    "deployment__isnull",  # BooleanFilter
#    "tags",  # MultipleChoiceFilter
#    "observation_type",  # CharFilter, método get_observation_type
#    "species",  # CharFilter, método get_species
#    "timestamp_error",  # BooleanFilter, método get_timestamp_error
#]

# Parametrización de filtros a testear
@pytest.mark.parametrize(
    "cp_id, filter_name,filter_value",
    [
        (33, "project", 33),
        (33, "collection", "47"),
    ]


#"owner",  # OwnCollectionBooleanFilter
#"research_projects",
#"locations_map",
)
def test_trapper_client_classificator_filters(trapper_client, cp_id, filter_name, filter_value):
    method_name = f"get_by_{filter_name}"

    # Saltar si no hay método generado automáticamente
    if not hasattr(trapper_client.media, method_name):
        logging.debug(f"Method {method_name} not implemented, skipping...")
        pytest.skip(f"Method {method_name} not implemented")

    method = getattr(trapper_client.media, method_name)

    import inspect
    logging.info(trapper_client.media)
    logging.info(inspect.signature(trapper_client.media.get_by_project))

    # Ejecutar consulta
    deployments = method(cp_id, filter_value)

    # Validaciones generales
    _validate_objects(deployments)

    # Validaciones adicionales específicas
    if filter_name in VALIDATIONS:
        VALIDATIONS[filter_name](deployments.results, filter_value)

    logging.debug(f"Filter '{filter_name}' returned {len(deployments.results)} results.")


def test_trapper_client_media_get_all(trapper_client):
    try:
        deployments = trapper_client.media.get_all()
        assert False, "Not implemented yet"
    except NotImplementedError as e:
        assert True, f"Exception occurred: {e}"
    except Exception as e:
        print(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_media_get_by_classification_project(trapper_client):
    id_test = "33"
    try:
        media = trapper_client.media.get_by_classification_project(id_test)
        _validate_media(media)
        logging.debug(f"Found {len(media.results)} active media in classification project {id_test}.")
    except Exception as e:
        logging.debug(f"Exception occurred: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_media_get_by_classification_project_and_collection(trapper_client):
    id_test = "33"
    id_collection = "47"
    try:
        media = trapper_client.media.get_by_classification_project_and_collection(id_test, id_collection)
        #_validate_media(media)
        logging.debug(f"Found {len(media.results)} active media in classification project {id_test} that allow to {id_collection} collection.")
    except Exception as e:
        logging.debug(f"Exception occurred: {e}")
        assert False, f"Exception occurred: {e}"



def _test_trapper_client_media_download_by_classification_project(trapper_client):
    id_test = "33"
    try:
        media_file_dir = trapper_client.media.download_by_classification_project(id_test, zip_filename_base="test_media_cp_33")
        assert media_file_dir.is_dir(), f"{media_file_dir} is not a directory"
        zip_files = list(media_file_dir.glob("*.zip"))
        assert len(zip_files) > 0, f".zip files not found in  {media_file_dir}"
        logging.debug(f"Media files in classification project {id_test} were stored in {media_file_dir}.")
    except Exception as e:
        logging.debug(f"Exception occurred: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_media_get_by_classification_project_only_animals(trapper_client):
    id_test = "33"
    try:
        media = trapper_client.media.get_by_classification_project_only_animals(id_test)
        _validate_media(media)
        logging.debug(f"Found {len(media.results)} active media in classification project {id_test}.")
    except Exception as e:
        logging.debug(f"Exception occurred: {e}")
        assert False, f"Exception occurred: {e}"

"""def test_trapper_client_media_get_by_classification_project_only_animals(trapper_client) -> T:
    id_test = "33"
    try:
        media = trapper_client.media.get_by_classification_project_only_animals(id_test)
        _validate_media(media)
        logging.debug(f"Found {len(media.results)} active media in classification project {id_test}.")
    except Exception as e:
        logging.debug(f"Exception occurred: {e}")
        assert False, f"Exception occurred: {e}"
"""

"""
   def _trapper_client_media_download_by_classification_project_only_animals(self, cp_id: int, query: dict = None, zip_filename_base: str = None):
download_by_classification_project
"""