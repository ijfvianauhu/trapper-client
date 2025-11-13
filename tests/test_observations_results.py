import logging
import pytest
from dotenv import load_dotenv

from tests.helpers import run_test_by_filters, validate_objects, make_validator
from tests.test_media import validate_project
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperObservationResults, TrapperClassification, TrapperUserClassification, \
    TrapperAIClassification, ClassificationResultsAgg, TrapperObservationResultsCTDP, TrapperObservationResultsTrapper


#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

VALIDATIONS = {
    "pk": make_validator("pk", single=True),
    #"project": make_validator("classification_project"), --> no devuelve campo con nombre del projecto
    "deployment": make_validator("deploymentID"),
    #"status": make_validator("status"),
    #"status_ai": make_validator("status"),
    "bboxes": make_validator("bboxX", op="!="),
    "rdate_from": make_validator("updated_at", op=">=", date_only=True),
    "rdate_to": make_validator("updated_at", op="<=", date_only=True),
}

# Parametrización de filtros a testear
@pytest.mark.parametrize(
    "filter_name,filter_values,expected_values",
    [
        #"pk",  # int → Identificador único del registro (primary key).
        #("pk", [33,60676], 606766),
        #"project",  # int → ID del proyecto de clasificación (project__pk).
        #("project", [33,33], "WICP_01_CP_ZOO"),
        #"owner",  # bool → Si true, devuelve recursos propiedad o gestionados por el usuario.
        #"deployment",  # int o list[int] → Filtra por uno o varios deployments (resource__deployment).
        # ("deployment", [33,898], "r9999-dona_0036"),
        #"collection",  # int o list[int] → Filtra por colecciones dentro del proyecto.
        # ("collection", [33,47], 47),
        #"locations_map",  # dict / custom → Filtro geográfico según BaseLocationsMapFilter.
        #"status",  # bool → Filtra clasificaciones activas/inactivas.
        # ("status", [33,True], True),
        #"status_ai",  # bool → Filtra por estado de clasificación automática (IA).
        #("status_ai", True, True),
        #"rdate_from",  # str (YYYY-MM-DD) → Fecha mínima de captura (>=).
        #("rdate_from", "2025-03-13", "2025-03-13"),
        #"rdate_to",  # str (YYYY-MM-DD) → Fecha máxima de captura (<=).
        #("rdate_to", "2025-02-13", "2025-02-13"),
        #"rtime_from",  # str (HH:MM) → Hora mínima dentro del día.
        #"rtime_to",  # str (HH:MM) → Hora máxima dentro del día.
        #"ftype",  # str → Tipo de recurso (image, video, etc.).
        #"classified",  # bool → True: tiene clasificaciones humanas; False: no tiene.
        #"classified_ai",  # bool → True: tiene clasificaciones de IA; False: no tiene.
        #"bboxes",  # bool → True: contiene bounding boxes (detecciones).
        ("bboxes", [33,""], "None"),
        #"species",  # int o list[int] → Filtra por especie (dynamic_attrs__species).
        #"observation_type",  # str → Tipo de observación (ObservationType.get_all_choices()).
        #"sex",  # str → Sexo del animal (SpeciesSex.get_all_choices()).
        #"age",  # str → Edad del animal (SpeciesAge.get_all_choices()).
    ]
)
def test_trapper_client_collection_filters(trapper_client, filter_name, filter_values, expected_values):
    run_test_by_filters(trapper_client, filter_name, filter_values, expected_values,
                        "observations.results", TrapperObservationResultsCTDP, VALIDATIONS)

def _test_trapper_client_observations_get_all(trapper_client):
    cp_id = 33
    try:
        observations = trapper_client.observations.results.get_all(cp_id)
        assert False, "This method is not implemented yet."
    except Exception as e:
        assert True, f"Exception occurred: {e}"

def _test_trapper_client_observations_get(trapper_client):
    try:
        cp_id = 33
        observations = trapper_client.observations.results.get(cp_id)
        assert False, "This method is not implemented yet."
    except Exception as e:
        assert True, f"Exception occurred: {e}"

def _test_trapper_client_observations_results_by_collection_camtrap(trapper_client):
    cp_id = 33
    c_id = 47
    try:
        observations = trapper_client.observations.results.get_by_collection(cp_id, c_id)
        logging.info(observations)
        validate_objects(observations, expected_type=TrapperObservationResultsCTDP)
        logging.info(f"Found {len(observations.results)} active observations whose collection is {c_id}.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_observations_results_get_by_collection_trapper(trapper_client):
    cp_id = 33
    c_id = 47
    query = {"camtrapdp": "False"}

    try:
        observations = trapper_client.observations.results.get_by_collection(cp_id, c_id, query=query)
        logging.info(observations)
        validate_objects(observations, expected_type=TrapperObservationResultsTrapper)
        logging.info(f"Found {len(observations.results)} active observations whose collection is {c_id}.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"
