import json
from pathlib import Path

import pyarrow as pa
import pytest
import requests


REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / "tests" / "fixtures" / "reference" / "catalog.json"


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def iter_active_fixtures():
    catalog = load_catalog()
    for entry in catalog["entries"]:
        if entry["kind"] != "fixture" or not entry["active"]:
            continue
        path = CATALOG_PATH.parent / entry["path"]
        yield json.loads(path.read_text(encoding="utf-8"))


def fixture_ids(fixtures):
    return [fixture["id"] for fixture in fixtures]


def build_request_payload(fixture: dict, engine: str) -> dict:
    payload = {
        "model": fixture["payload"]["model"],
        "model_name": fixture["id"],
        "engine": engine,
        "solver": fixture["solver"],
    }
    return payload


def run_pyomo_direct(fixture: dict) -> dict:
    pytest.importorskip("pyomo.environ")
    from service.optimization_service.python.pyomo.service.opt_solver import PyomoSolver

    params = dict(fixture["payload"]["model"])
    params["solver"] = fixture["solver"]
    solver = PyomoSolver()
    return solver.run(params)


def run_gateway_case(fixture: dict, engine: str, endpoint: str = "http://127.0.0.1:8000/compute") -> tuple[int, dict]:
    pytest.importorskip("arrow_table_dict_conversion")
    from arrow_table_dict_conversion import dict_to_pa_table, unpack_pa_table_dict

    request_payload = build_request_payload(fixture, engine)
    ipc_table = dict_to_pa_table(request_payload)

    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, ipc_table.schema) as writer:
        writer.write(ipc_table)

    response = requests.post(
        endpoint,
        data=sink.getvalue().to_pybytes(),
        headers={"Content-Type": "application/vnd.apache.arrow.stream"},
        timeout=120,
    )

    if response.headers.get("content-type", "").startswith("application/vnd.apache.arrow.stream"):
        reader = pa.ipc.open_stream(response.content)
        result = unpack_pa_table_dict(reader.read_all())
    else:
        result = {"error_message": response.text}
    return response.status_code, result


def assert_reference_result(result: dict, fixture: dict) -> None:
    expected = fixture["expected"]

    assert result.get("success", True) is not False, result
    assert "error_message" not in result, result
    assert str(result.get("status", "")).lower() == expected["status"].lower(), result

    objective = expected["objective"]
    assert abs(float(result["obj_val"]) - float(objective["value"])) <= float(objective["atol"]), result

    expected_solution = expected.get("solution")
    if expected_solution is None:
        return

    actual_solution = result.get("solution")
    assert actual_solution is not None, result
    assert len(actual_solution) == len(expected_solution["value"]), result
    atol = float(expected_solution["atol"])
    for actual, expected_value in zip(actual_solution, expected_solution["value"]):
        assert abs(float(actual) - float(expected_value)) <= atol, result
