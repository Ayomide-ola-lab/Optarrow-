import pyarrow as pa
import requests
import time
import pytest
import utils.network_check as ncheck
from service.optimization_service.python.pyomo.service.opt_solver import PyomoSolver
from arrow_table_dict_conversion import dict_to_pa_table, unpack_pa_table_dict
import tracemalloc

# Simple product-mix LP: maximize 5*x0 + 12*x1
# subject to: 20*x0 + 10*x1 <= 200, 10*x0 + 20*x1 <= 120, 10*x0 + 30*x1 <= 150
# optimal: x0=6, x1=3, obj=66
model_data = {
    'A': {
        'col': [0, 1, 0, 1, 0, 1],
        'row': [0, 0, 1, 1, 2, 2],
        'val': [20.0, 10.0, 10.0, 20.0, 10.0, 30.0]
    },
    'b': [200.0, 120.0, 150.0],
    'c': [5.0, 12.0],
    'lb': [0.0, 0.0],
    'ub': [1000.0, 1000.0],
    'osense': 'max',
    'csense': ['L', 'L', 'L']
}

solvers = [
    pytest.param({"solver_name": "Gurobi", "solver_type": "LP", "time_limit": 60, "solver_params": {}}, id="Gurobi"),
    pytest.param({"solver_name": "GLPK", "solver_type": "LP", "solver_params": {}}, id="GLPK"),
    pytest.param({"solver_name": "HiGHS", "solver_type": "LP", "solver_params": {"presolve":"on", "infinite_cost":1e+18}}, id="HiGHS w/Params"),
    pytest.param({"solver_name": "HiGHS", "solver_type": "LP", "solver_params": {}}, id="HiGHS"),
]

@pytest.mark.parametrize("solver", solvers)
def test_pyomo_service(solver):
    if ncheck.check_socket("127.0.0.1", 8000) is False:
        pytest.skip("Server is not started")
    url = "http://127.0.0.1:8000/compute"

    ipc_dict = {
        "model": model_data,
        "model_name": "product_mix_lp",
        "engine": "Python",
        "time_limit": 60,
        "solver": solver
    }
    ipc_table = dict_to_pa_table(ipc_dict)

    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, ipc_table.schema) as writer:
        writer.write(ipc_table)
    ipc_bytes = sink.getvalue().to_pybytes()

    headers = {"Content-Type": "application/vnd.apache.arrow.stream"}

    pre = time.time()
    response = requests.post(url, data=ipc_bytes, headers=headers)

    reader = pa.ipc.open_stream(response.content)
    table = reader.read_all()
    resdict = unpack_pa_table_dict(table)
    print(resdict)
    assert "Exception" not in str(resdict)
    assert resdict.get("obj_val") > 0
    assert resdict.get("status") == "optimal"
    assert "Error" not in str(resdict)
    post = time.time()
    print(f"Time diff: {post - pre:.2f}s")


@pytest.mark.parametrize("solver", solvers)
def test_pyomo_service_json(solver):
    tracemalloc.start()
    if ncheck.check_socket("127.0.0.1", 8000) is False:
        pytest.skip("Server is not started")
    url = "http://127.0.0.1:8000/computeJSON"

    ipc_dict = {
        "model": model_data,
        "model_name": "product_mix_lp",
        "engine": "PYTHON",
        "solver": solver
    }
    headers = {"Content-Type": "application/json"}

    pre = time.time()
    response = requests.post(url, json=ipc_dict, headers=headers)
    cont = response.json()
    print(cont)
    assert "Exception" not in str(cont)
    assert cont.get("obj_val") > 0
    assert cont.get("status") == "optimal"
    assert "Error" not in str(cont)
    print(f"Time diff: {time.time() - pre:.2f}s")
    tracemalloc.stop()


@pytest.mark.parametrize("solver", solvers)
def test_pyomo_lp_no_server(solver):
    tracemalloc.start()
    params = dict(model_data)
    params["solver"] = solver
    solver_inst = PyomoSolver()
    result = solver_inst.run(params)
    print(result)
    assert result.get("success") is not False
    assert result.get("obj_val") > 0
    assert "Exception" not in str(result)
    assert "Error" not in str(result)
    assert result.get("solution") is not None
    print(f"Mem used: Peak: {tracemalloc.get_traced_memory()[1] / 1024:.1f} KiB")
    tracemalloc.stop()
