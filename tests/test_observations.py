import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperCPObservation, TrapperClassification, TrapperUserClassification, \
    TrapperAIClassification, ClassificationResultsAgg


#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

def _validate_observations(observations, expected_type=TrapperCPObservation):
    """Common validation for deployments responses."""
    assert hasattr(observations, "results")
    assert hasattr(observations, "pagination")

    if observations.results:  # only if results is not empty
        assert isinstance(observations.results[0], expected_type)

def _test_trapper_client_observations_get_all(trapper_client):
    try:
        observations = trapper_client.observations.get_all()
        _validate_observations(observations, expected_type=TrapperClassification)
        logging.info(f"Found {len(observations.results)} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_observations_get(trapper_client):
    try:
        observations = trapper_client.observations.get()
        _validate_observations(observations, expected_type=TrapperClassification)
        assert observations.pagination.page == 1
        logging.info(f"Found {len(observations.results)} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_observations_get_by_filter_rp(trapper_client):
    try:
        observations = trapper_client.observations.get_all(query={"project":"33"})
        _validate_observations(observations, expected_type=TrapperClassification)
        assert observations.pagination.page == 1
        logging.info(f"Found {len(observations.results)} active observations.")
        logging.info(f"Found {observations.results[0]} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_observations_get_all_user(trapper_client):
    try:
        observations = trapper_client.observations.get_all_user_classifications()
        _validate_observations(observations, expected_type=TrapperUserClassification)
        logging.debug(f"Found {len(observations.results)} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_observations_get_user(trapper_client):
    try:
        observations = trapper_client.observations.get_user_classifications()
        _validate_observations(observations, expected_type=TrapperUserClassification)
        assert observations.pagination.page == 1
        logging.info(f"Found {len(observations.results)} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_observations_get_all_ai(trapper_client):
    try:
        observations = trapper_client.observations.get_all_ai_classifications()
        _validate_observations(observations, expected_type=TrapperAIClassification)
        logging.debug(f"Found {len(observations.results)} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_observations_get_ai(trapper_client):
    try:
        observations = trapper_client.observations.get_ai_classifications()
        _validate_observations(observations, expected_type=TrapperAIClassification)
        assert observations.pagination.page == 1
        logging.info(f"Found {len(observations.results)} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

    def get_all_ai_classifications_by_classification_project(self, cp_id: int, query: Dict[str, Any] = None, filter_fn: Callable[[T], bool] = None) -> T:
        return self.get_all(query, filter_fn, f"/media_classification/api/ai-classifications/results/{cp_id}/")

    def get_ai_classificationss_by_classification_project(self, cp_id: int, query: Dict[str, Any] = None, filter_fn: Callable[[T], bool] = None) -> T:
        return self.get(query, filter_fn, f"/media_classification/api/ai-classifications/results/{cp_id}/")


def _test_trapper_client_observations_get_all_by_classification_project(trapper_client):
    id_test = 33
    try:
        resources = trapper_client.observations.get_all_by_classification_project(id_test)
        _validate_observations(resources, expected_type=TrapperCPObservation)
        logging.info(f"Found {len(resources.results)} active observations in classification project {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_observations_get_by_classification_project(trapper_client):
    id_test = 33
    try:
        resources = trapper_client.observations.get_by_classification_project(id_test)
        logging.info(resources.results[0])
        _validate_observations(resources, expected_type=TrapperCPObservation)
        logging.info(f"Found {len(resources.results)} active observations in classification project {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_observations_get_all_ai_by_classification_project(trapper_client):
    id_test = 33
    try:
        resources = trapper_client.observations.get_all_ai_classifications_by_classification_project(id_test)
        _validate_observations(resources)
        logging.info(f"Found {len(resources.results)} active ai observations in classification project {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_observations_get_ai_by_classification_project(trapper_client):
    id_test = 33
    try:
        resources = trapper_client.observations.get_ai_classificationss_by_classification_project(id_test)
        _validate_observations(resources)
        logging.info(f"Found {len(resources.results)} active ai observations in classification project {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"


def test_trapper_client_observations_get_all_aggegated_by_classification_project(trapper_client):
    id_test = 33
    try:
        resources = trapper_client.observations.get_all_aggregated_classifications_by_classification_project(id_test)
        _validate_observations(resources, expected_type=ClassificationResultsAgg)
        logging.info(f"Found {len(resources.results)} active ai observations in classification project {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_observations_get_aggregated_by_classification_project(trapper_client):
    id_test = 33
    try:
        resources = trapper_client.observations.get_aggregated_classifications_by_classification_project(id_test)
        _validate_observations(resources, expected_type=ClassificationResultsAgg)
        logging.info(f"Found {len(resources.results)} active ai observations in classification project {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"