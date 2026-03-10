import pyarrow as pa
import requests

ipc_dict = {
  "model": {
    "A": {
      "row": [0, 0, 1, 1, 2, 2],
      "col": [0, 1, 0, 1, 0, 1],
      "val": [20, 10, 10, 20, 10, 30]
    },
    "b": [200, 120, 150],
    "c": [5, 12],
    "lb": [0, 0],
    "csense": ["L", "L", "L"], # 'L' for less than or equal to constraints
    "osense": "max"
  },
  "model_name": "product_mix_lp",
  "engine": "julia", # Using Julia as the optimization engine, also supports Python
  "solver": {
    "solver_name": "HiGHS", # Using HiGHS solver for LP problems, also supports other solvers
    "solver_type": "LP", # Specify the solver type as LP
    "solver_params": {} # Additional solver parameters can be added here
  }
}

# Convert the dictionary to an Arrow table for IPC serialization
pa_arrays = [pa.array([v]) for v in ipc_dict.values()]
table = pa.Table.from_arrays(pa_arrays, names=list(ipc_dict.keys()))

# Serialize the table to IPC stream bytes
sink = pa.BufferOutputStream()
with pa.ipc.new_stream(sink, table.schema) as writer:
    writer.write(table)
ipc_bytes = sink.getvalue().to_pybytes()

# Send the IPC stream bytes to the server
headers = {"Content-Type": "application/vnd.apache.arrow.stream"}
response = requests.post("http://localhost:8000/compute", data=ipc_bytes, headers=headers)

# Check if the response is successful
if response.status_code != 200:
    print(f"Error: {response.status_code} - {response.text}")
# response is ipc stream
reader = pa.ipc.open_stream(response.content)
result_table = reader.read_all()
result_dict = {name: result_table.column(name).to_pylist() for name in result_table.column_names}
print(result_dict)
