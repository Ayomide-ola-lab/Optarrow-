import requests, time
import pytest, tracemalloc
import utils.network_check as ncheck
import pyarrow as pa
from service.optimization_service.python.pyomo.service.opt_solver import PyomoSolver
from arrow_table_dict_conversion import dict_to_pa_table, unpack_pa_table_dict

osense = "min"
model_name = "test_qp"
engine = "PYthON"

model = {
    "Q": {
        "row": [0, 0, 2, 1, 2],
        "col": [0, 2, 0, 1, 2],
        "val": [2, 1, 1, 4, 6]
    },
    "c": [1, -2, 4],
    "A": {
        "row": [0, 0, 0],
        "col": [0, 1, 2],
        "val": [2, 3, 4]
    },
    "b": [5],
    "G": {
        "row": [0, 0, 0, 1, 1, 1],
        "col": [0, 1, 2, 0, 1, 2],
        "val": [3, 4, -2, 3, -2, -1]
    },
    "h": [10, -2],
    "lb": [0, 1, 0],
    "ub": [5, 5, 5],
    "osense": osense
}

solvers = [
    pytest.param({"solver_name": "Gurobi", "solver_type": "QP", "solver_params": {}}, id="Gurobi"),
    pytest.param({"solver_name": "HiGHS", "solver_type": "QP", "solver_params": {}}, id="HiGHS"),
]

@pytest.mark.parametrize("solver", solvers)
def test_pyomo_service(solver):
    if ncheck.check_socket("127.0.0.1", 8000) is False:
        pytest.skip("Server is not started")
    url = "http://127.0.0.1:8000/compute"

    ipc_dict = {
        "model": model,
        "model_name": model_name,
        "engine": engine,
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
    print(f"Time diff: {time.time() - pre:.2f}s")

    assert "Exception" not in str(resdict)
    assert resdict.get("obj_val") > 0
    assert resdict.get("status").lower() == "optimal"
    assert "Error" not in str(resdict)


@pytest.mark.parametrize("solver", solvers)
def test_pyomo_service_json(solver):
    tracemalloc.start()
    if ncheck.check_socket("127.0.0.1", 8000) is False:
        pytest.skip("Server is not started")
    url = "http://127.0.0.1:8000/computeJSON"

    ipc_dict = {
        "model": model,
        "model_name": model_name,
        "engine": "python",
        "solver": solver
    }
    headers = {"Content-Type": "application/json"}
    pre = time.time()
    response = requests.post(url, json=ipc_dict, headers=headers)
    cont = response.json()
    print(cont)
    assert "Exception" not in str(cont)
    assert cont.get("obj_val") > 0
    assert cont.get("status").lower() == "optimal"
    assert "Error" not in str(cont)
    print(f"Time diff: {time.time() - pre:.2f}s")
    tracemalloc.stop()


@pytest.mark.parametrize("solver", solvers)
def test_pyomo_qp_no_server(solver):
    params = dict(model)
    params["solver"] = solver
    solver_inst = PyomoSolver()
    result = solver_inst.run(params)
    assert True == result.get("success")
    assert "Exception" not in str(result)
    assert "Error" not in str(result)
    print(result)
