import logging
import pytest

def validate_objects(deployments, expected_type):
    """Common validation for deployments responses."""
    assert hasattr(deployments, "results")
    assert hasattr(deployments, "pagination")

    if deployments.results:  # solo si hay resultados
        assert isinstance(deployments.results[0], expected_type)

def run_test_by_filters(trapper_client, filter_name, filter_value, component_name, object_type, VALIDATIONS):

    method_name = f"get_by_{filter_name}"

    component = getattr(trapper_client, component_name)  # obtiene trapper_client.locations

    if not hasattr(component, method_name):
        logging.debug(f"Method {method_name} not implemented, skipping...")
        pytest.skip(f"Method {method_name} not implemented")

    method = getattr(component, method_name)
    response = method(filter_value)
    validate_objects(response, object_type)

    if filter_name in VALIDATIONS:
        VALIDATIONS[filter_name](response.results, filter_value)

    logging.debug(f"Filter '{filter_name}' returned {len(response.results)} results.")

def validate_pk(results, expected):
    assert len(results) == 1
    assert all(d.pk == expected for d in results)

def validate_name(results, expected):
    assert all(d.name == expected for d in results)

def validate_acronym(results, expected):
    assert all(d.name == expected for d in results)

def validate_rdata_from(results, expected):
    from datetime import datetime
    expected_date = datetime.fromisoformat(expected)
    assert all(d.date_recorded >= expected_date for d in results)
