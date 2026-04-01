import pytest

from tests.reference_benchmarks.helpers import (
    assert_reference_result,
    fixture_ids,
    iter_active_fixtures,
    run_pyomo_direct,
)


FIXTURES = list(iter_active_fixtures())


@pytest.mark.parametrize("fixture", FIXTURES, ids=fixture_ids(FIXTURES))
def test_reference_problem_with_pyomo_direct(fixture):
    result = run_pyomo_direct(fixture)
    assert_reference_result(result, fixture)
