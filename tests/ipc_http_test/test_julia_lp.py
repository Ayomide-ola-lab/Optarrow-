import time
import pytest
import requests
import pyarrow as pa
from arrow_table_dict_conversion import dict_to_pa_table
import utils.network_check as ncheck

# Simple product-mix LP: maximize 5*x0 + 12*x1
# subject to: 20*x0 + 10*x1 <= 200, 10*x0 + 20*x1 <= 120, 10*x0 + 30*x1 <= 150
# optimal: x0=6, x1=3, obj=66
req_params = {
    "model": {
        "A": {
            "col": [0, 1, 0, 1, 0, 1],
            "row": [0, 0, 1, 1, 2, 2],
            "val": [20.0, 10.0, 10.0, 20.0, 10.0, 30.0]
        },
        "b": [200.0, 120.0, 150.0],
        "c": [5.0, 12.0],
        "lb": [0.0, 0.0],
        "ub": [1000.0, 1000.0],
        "osense": "max",
        "csense": ["L", "L", "L"]
    },
    "model_name": "product_mix_lp",
    "engine": "julia",
    "time_limit": 60,
}

solvers = [
    {"solver_name": "GLPK", "solver_type": "LP", "solver_params": {}},
    {"solver_name": "HiGHS", "solver_type": "LP", "solver_params": {"presolve": "on", "infinite_cost": 1e+18}},
    {"solver_name": "HiGHS", "solver_type": "LP", "solver_params": {}},
    {"solver_name": "Gurobi", "solver_type": "LP", "solver_params": {}},
    {"solver_name": "MOSEK", "solver_type": "LP", "solver_params": {}},
    {"solver_name": "Hypatia", "solver_type": "LP", "solver_params": {"tol_inconsistent": 1e-8}},
    {"solver_name": "Hypatia", "solver_type": "LP", "solver_params": {"presolve": True, "dual": True, "primal": True}}
]


@pytest.mark.parametrize("solver", solvers, ids=[s["solver_name"] for s in solvers])
def test_julia_flow(solver):
    if ncheck.check_socket("127.0.0.1", 8000) is False:
        pytest.skip("Server is not started")
    url = "http://127.0.0.1:8000/compute"

    req_params["solver"] = solver
    ipc_table = dict_to_pa_table(req_params)

    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, ipc_table.schema) as writer:
        writer.write(ipc_table)
    ipc_bytes = sink.getvalue().to_pybytes()

    headers = {"Content-Type": "application/vnd.apache.arrow.stream"}
    pre = time.time()
    response = requests.post(url, data=ipc_bytes, headers=headers)
    print(f"Request took {time.time() - pre:.2f}s")

    if solver["solver_name"] in ["Gurobi", "MOSEK"]:
        assert response.status_code == 500
        assert "license" in response.text.lower()
    elif solver["solver_name"] == "Hypatia" and solver["solver_params"].get("presolve", 0) != 0:
        assert response.status_code == 500
        assert "ErrorException" in response.text
    else:
        assert response.status_code == 200
        reader = pa.ipc.open_stream(response.content)
        result_table = reader.read_all()
        assert result_table.num_rows > 0
        assert "solution" in result_table.column_names
        assert "obj_val" in result_table.column_names
        solution = result_table.column("solution")[0].as_py()
        objective_value = result_table.column("obj_val")[0].as_py()
        assert solution is not None
        assert objective_value is not None
        print(f"Objective value: {objective_value} for solver {solver['solver_name']}")
        assert len(solution) == len(req_params["model"]["c"])
