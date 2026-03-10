from scipy.io import loadmat
from scipy import sparse
import numpy as np
import requests
import pyarrow as pa
import os
import time

def download_qplib(instance_id=None, save_path=None):
    if instance_id is None:
        raise ValueError("Instance ID must be provided")
    url = f"https://qplib.zib.de/qplib/{instance_id}.qplib"
    if save_path is None:
        save_path = f"{instance_id}.qplib"
    r = requests.get(url)
    r.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(r.content)
    print(f"Downloaded {instance_id} to {save_path}")
    return save_path


def read_qplib(path):
    with open(path, "r") as f:
        lines = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
    
    ptr = 0
    name = lines[ptr]; ptr += 1
    probtype = lines[ptr]; ptr += 1
    sense = lines[ptr]; ptr += 1
    
    nvar = int(lines[ptr].split()[0]); ptr += 1
    ncon = int(lines[ptr].split()[0]); ptr += 1
    nquad = int(lines[ptr].split()[0]); ptr += 1
    
    # Quadratic terms
    Q = np.zeros((nvar, nvar))
    for _ in range(nquad):
        i, j, v = lines[ptr].split()
        i, j, v = int(i)-1, int(j)-1, float(v)
        if i == j:
            # diagonal must be doubled for 0.5 x^T Q x convention
            Q[i, i] += 2.0 * v
        else:
            # off-diagonals mirrored (Q should be symmetric)
            Q[i, j] += v
            Q[j, i] += v
        ptr += 1
    
    # Linear objective
    default_c = float(lines[ptr].split()[0]); ptr += 1
    nlinobj = int(lines[ptr].split()[0]); ptr += 1
    c = np.full(nvar, default_c)
    for _ in range(nlinobj):
        j, v = lines[ptr].split()
        c[int(j)-1] = float(v)
        ptr += 1
    const_obj = float(lines[ptr].split()[0]); ptr += 1
    
    # Linear constraints
    nlincon = int(lines[ptr].split()[0]); ptr += 1
    A = np.zeros((ncon, nvar))
    for _ in range(nlincon):
        i, j, v = lines[ptr].split()
        A[int(i)-1, int(j)-1] = float(v)
        ptr += 1
    
    inf_val = float(lines[ptr].split()[0]); ptr += 1
    
    # LHS
    default_lhs = float(lines[ptr].split()[0]); ptr += 1
    n_lhs = int(lines[ptr].split()[0]); ptr += 1
    lhs = np.full(ncon, default_lhs)
    for _ in range(n_lhs):
        i, v = lines[ptr].split()
        lhs[int(i)-1] = float(v)
        ptr += 1
    
    # RHS
    default_rhs = float(lines[ptr].split()[0]); ptr += 1
    n_rhs = int(lines[ptr].split()[0]); ptr += 1
    rhs = np.full(ncon, default_rhs)
    for _ in range(n_rhs):
        i, v = lines[ptr].split()
        rhs[int(i)-1] = float(v)
        ptr += 1
    
    # Bounds
    default_lb = float(lines[ptr].split()[0]); ptr += 1
    n_lb = int(lines[ptr].split()[0]); ptr += 1
    lb = np.full(nvar, default_lb)
    for _ in range(n_lb):
        j, v = lines[ptr].split()
        lb[int(j)-1] = float(v)
        ptr += 1
    
    default_ub = float(lines[ptr].split()[0]); ptr += 1
    n_ub = int(lines[ptr].split()[0]); ptr += 1
    ub = np.full(nvar, default_ub)
    for _ in range(n_ub):
        j, v = lines[ptr].split()
        ub[int(j)-1] = float(v)
        ptr += 1

    Q = sparse.coo_matrix(Q)
    Q={
        "val": Q.data.tolist(),
        "row": Q.row.flatten().tolist(),
        "col": Q.col.flatten().tolist(),
    }
    A = sparse.coo_matrix(A)
    A = {
        "val": A.data.tolist(),
        "row": A.row.flatten().tolist(),
        "col": A.col.flatten().tolist(),
    }

    return dict(name=name, Q=Q, c=c, G=A, h=rhs, lb=lb, ub=ub)


if __name__ == "__main__":
    # download QPLIB_10050
    path = download_qplib("QPLIB_10050")

    # Parse
    data = read_qplib(path)
    print("Problem:", data["name"])
    model_data = {
    "Q": data["Q"],
    "G": data["G"],
    "h": data["h"].flatten().tolist(),
    "c": data["c"].flatten().tolist(),
    "osense": "min",
    }
    ipc_dict = {
        "model": model_data,
        "model_name": data["name"],
        "engine": "julia",
        "solver": {
        "solver_name": "HiGHS",
        "solver_type": "QP",
        "solver_params": {}
        }
    }
    
    # Prepare Arrow IPC stream
    pa_arrays = [pa.array([v]) for v in ipc_dict.values()]
    ipc_tables = pa.Table.from_arrays(pa_arrays, names=list(ipc_dict.keys()))

    # Serialize to Arrow stream
    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, ipc_tables.schema) as writer:
        writer.write(ipc_tables)
    ipc_bytes = sink.getvalue().to_pybytes()

    # Send request
    headers = {
            "Content-Type": "application/vnd.apache.arrow.stream"
        }
    start_time = time.time()
    response = requests.post("http://localhost:8000/compute", data=ipc_bytes, headers=headers)
    end_time = time.time()
    print(f"Time taken for request: {end_time - start_time:.2f} seconds") 

    # Handle the response
    if response.status_code == 200:
        response_data = response.content
        response_table = pa.ipc.open_stream(response_data).read_all()
        print("Objective value:", response_table['obj_val'][0])
        print("Status:", response_table['status'][0])
        # print("Solution:", response_table['solution'][0])
    else:
        response_data = response.content
        response_table = pa.ipc.open_stream(response_data).read_all()
        print("Error message:", response_table['error_message'][0])

    # Delete downloaded files
    os.remove(path)