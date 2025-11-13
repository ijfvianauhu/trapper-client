import logging
import pytest

logger = logging.getLogger(__name__)

def validate_objects(deployments, expected_type):
    """Common validation for deployments responses."""
    assert hasattr(deployments, "results")
    assert hasattr(deployments, "pagination")

    if deployments.results:  # solo si hay resultados
        assert isinstance(deployments.results[0], expected_type)

def resolve_component(root, dotted_name):
    """
    Resuelve rutas anidadas de atributos separados por puntos, por ejemplo:
    'aiobservations.results' -> getattr(getattr(root, 'aiobservations'), 'results')
    """
    component = root
    for attr in dotted_name.split('.'):
        try:
            component = getattr(component, attr)
        except AttributeError:
            raise AttributeError(f"Cannot resolve '{attr}' inside '{component.__class__.__name__}'")
    return component


def run_test_by_filters(trapper_client, filter_name, filter_values, expected_values, component_name, object_type, VALIDATIONS, query={}):

    method_name = f"get_by_{filter_name}"

    component = resolve_component(trapper_client, component_name)

    if not hasattr(component, method_name):
        logger.debug(f"Method {method_name} not implemented, skipping...")
        pytest.skip(f"Method {method_name} not implemented")

    method = getattr(component, method_name)

    if not isinstance(filter_values, (list, tuple)):
        filter_values = [filter_values]

    if not isinstance(expected_values, (list, tuple)):
        expected_values = [expected_values]

    response = method(*filter_values,query=query)
    logger.debug(response)
    validate_objects(response, object_type)

    if filter_name in VALIDATIONS:
        VALIDATIONS[filter_name](response.results, filter_values, expected_values)

    logging.debug(f"Filter '{filter_name}' returned {len(response.results)} results.")

from datetime import datetime

def validate_field(results, field_name, expected_value, op="==", date_only=False):
    """
    Valida que todos los objetos en 'results' cumplan la condición especificada.

    Parámetros
    ----------
    results : list
        Lista de objetos devueltos por el test.
    field_name : str
        Nombre del atributo a validar (por ejemplo, 'pk', 'status', etc.).
    expected_value : any
        Valor esperado para la comparación (puede ser None).
    op : str
        Operador de comparación: '==', '!=', '>=', '<=' (por defecto '==').
    date_only : bool
        Si True, compara solo la parte de fecha (ignora hora).
    """
    for d in results:
        value = getattr(d, field_name)

        # Normalizamos cadenas vacías a None
        if value == "":
            value = None

        # Si es datetime y queremos solo la fecha
        if date_only and hasattr(value, "date"):
            value = value.date()
            if isinstance(expected_value, str):
                expected_value = datetime.strptime(expected_value, "%Y-%m-%d").date()

        # Comparaciones seguras según el operador
        if op == "==":
            assert value == expected_value, f"{field_name}={value!r} != {expected_value!r}"
        elif op == "!=":
            assert value != expected_value, f"{field_name}={value!r} == {expected_value!r}"
        elif op == ">=":
            assert (
                value is not None and expected_value is not None and value >= expected_value
            ), f"{field_name}={value!r} < {expected_value!r}"
        elif op == "<=":
            assert (
                value is not None and expected_value is not None and value <= expected_value
            ), f"{field_name}={value!r} > {expected_value!r}"
        else:
            raise ValueError(f"Unsupported operator: {op}")


def make_validator(field, op="==", date_only=False, single=False):
    def _validate(results, filter_values, expected_values):
        if single:
            assert len(results) == 1, f"Expected one result for {field}"
        validate_field(results, field, expected_values[0], op=op, date_only=date_only)
    return _validate


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
