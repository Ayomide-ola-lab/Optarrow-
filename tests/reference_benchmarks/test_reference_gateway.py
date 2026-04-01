import pytest

from tests.reference_benchmarks.helpers import (
    assert_reference_result,
    fixture_ids,
    iter_active_fixtures,
    run_gateway_case,
)
from utils.network_check import check_socket


FIXTURES = list(iter_active_fixtures())


@pytest.mark.parametrize("fixture", FIXTURES, ids=fixture_ids(FIXTURES))
def test_reference_problem_through_gateway_python(fixture):
    if not check_socket("127.0.0.1", 8000):
        pytest.skip("Gateway server is not started")

    if "python" not in fixture["supported_engines"]:
        pytest.skip("Fixture is not enabled for the Python engine")

    status_code, result = run_gateway_case(fixture, engine="python")
    assert status_code == 200, result
    assert_reference_result(result, fixture)


@pytest.mark.parametrize("fixture", FIXTURES, ids=fixture_ids(FIXTURES))
def test_reference_problem_through_gateway_julia(fixture):
    if not check_socket("127.0.0.1", 8000):
        pytest.skip("Gateway server is not started")

    if "julia" not in fixture["supported_engines"]:
        pytest.skip("Fixture is not enabled for the Julia engine")

    status_code, result = run_gateway_case(fixture, engine="julia")
    assert status_code == 200, result
    assert_reference_result(result, fixture)
