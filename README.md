# OptArrow Computation Service

OptArrow website: https://optarrow.github.io/optArrow/


**OptArrow** is an optimization integration engine designed to seamlessly connect the Python and Julia ecosystems. It addresses the technical and structural challenges of building scalable, high-performance optimization pipelines across languages.

Requires Python and Julia, Python >= 3.12 and Julia >=1.11 Recommended

Integrated with poetry for unit testing and dependency management. The best practice is to use poetry to handle dependency and environment management.

Currently supported solvers:

- [GLPK](https://www.gnu.org/software/glpk/#TOCdownloading)(Not supported for QP problems)
- [GUROBI](https://www.gurobi.com/documentation/quickstart.html)
- [HiGHS](https://www.highs.dev/)
- [Mosek](https://docs.mosek.com/10.2/install/installation.html)
- [Hypatia](https://github.com/chriscoey/Hypatia.jl) (For Julia Only)

Please ensure that the executables for the solvers are properly installed and in the system PATH.

## 1. Clone the repository

Currently source code are required if you want to start without using `docker`. Clone the source code using `git` and `cd` into the project directory:

```bash
    git clone https://github.com/your-org/OptArrow.git
    cd OptArrow
```


## 2. Install Python and Julia

### 2.1 Install Python (>=3.12 recommended)
- **Windows**

  1. Download installer from [Python.org Downloads](https://www.python.org/downloads/).
  2. During installation, check **"Add Python to PATH"**.
  3. Verify installation:

     ```powershell
     python --version
     ```

- **MacOS**

  1. Use [Homebrew](https://brew.sh/):

     ```bash
     brew install python@3.12
     ```

  2. Or download directly from [Python.org](https://www.python.org/downloads/MacOS/).
  3. Verify installation:

     ```bash
     python3 --version
     ```

- **Linux (Debian/Ubuntu)**

  ```bash
  sudo apt update
  sudo apt install -y python3.12 python3.12-venv python3.12-dev
  python3.12 --version
  ```

- **Linux (Fedora/RHEL)**

  ```bash
  sudo dnf install python3.12 python3.12-devel
  python3.12 --version
  ```


### 2.2 Install Julia (>=1.11 recommended)

- **Windows / MacOS / Linux (generic)**

  1. Download binaries from [Julia Downloads](https://julialang.org/downloads/).
  2. Extract and place Julia in your desired folder.
  3. Add Julia `bin/` folder to PATH (on Windows via System Environment Variables, on Linux/MacOS by editing `~/.bashrc` or `~/.zshrc`).
  4. Verify installation:

     ```bash
     julia --version
     ```

- **Linux (Debian/Ubuntu quick install)**

  ```bash
  curl -fsSL https://install.julialang.org | sh
  ```

- **MacOS (Homebrew)**

  ```bash
  brew install julia
  ```


## 3. Install dependency

### 3.1 Install Pipx

[pipx](https://pipx.pypa.io/stable/) is a tool to install and run Python applications in isolated environments. Recommended for installing `poetry`.

```bash
pipx install poetry
```

-  **Windows**

1. Make sure you have **Python 3.12+** installed and added to PATH.
2. Open **PowerShell** and run:

```powershell
   py -m pip install --user pipx
   py -m pipx ensurepath
   ```

3. Restart PowerShell or your terminal so PATH changes take effect.
4. Verify installation:

   ```powershell
   pipx --version
   ```


-  **MacOS**

1. Ensure you have **Python 3.12+** installed (via [python.org](https://www.python.org/downloads/MacOS/) or Homebrew).
2. If using **Homebrew**, you can install pipx directly:

   ```bash
   brew install pipx
   pipx ensurepath
   ```

   Or install via pip:

   ```bash
   python3 -m pip install --user pipx
   python3 -m pipx ensurepath
   ```

3. Restart your terminal or run `source ~/.zshrc`.
4. Verify installation:

   ```bash
   pipx --version
   ```


-  **Linux (Debian/Ubuntu)**

1. Install dependencies:

   ```bash
   sudo apt update
   sudo apt install -y python3.12 python3.12-venv python3-pip
   ```

2. Install pipx:

   ```bash
   python3.12 -m pip install --user pipx
   python3.12 -m pipx ensurepath
   ```

3. Add `~/.local/bin` to your PATH if not already included:

   ```bash
   echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
   source ~/.bashrc
   ```

4. Verify installation:

   ```bash
   pipx --version
   ```

👉 On **Fedora / RHEL** you can install via DNF:

```bash
sudo dnf install pipx
pipx ensurepath
```

### 3.2 Install Python dependencies

Install `poetry` first. [Pipx](https://pipx.pypa.io/stable/installation/) can be used for installing `poetry`:

```bash
pipx install poetry
```

See [Poetry install](https://python-poetry.org/docs/) for more details about poetry.

Then in project root directory, run following command to install dependencies and create a virtual environment.

```bash
poetry install --no-root
```

Using pip directly or any other dependency management is not recommended in order to avoid unforseen issues.

### 3.3 Install Julia dependencies

#### Launch Julia in project mode

```bash
julia --project=./src/service/optimization_service/julia
```

This tells Julia to use the current folder's environment (Project.toml + Manifest.toml).

#### Install dependencies (only needed the first time)
Once inside Julia REPL:
```bash
julia> ]
(pkg) instantiate
```


## 4. Start all service instances (engines + gateway service)
You can use our start script to launch all services:
```bash
sh scripts/startAll.sh
```

If you want to start a specific service instance only, you can use the following commands:

- Start gateway service instance only
  ```bash
  sh scripts/startServer.sh
  ```
- Start python engine service instance only
  ```bash
  sh scripts/startPyEngine.sh
  ```
- Start julia engine service instance only
  ```bash
  sh scripts/startJulia.sh
  ```


## 5. Services are ready! 
Once the services are started properly and is able to communicate with each other, you can run an example using following Python script that solves a simple Linear Programming problem:

```python

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

```

And you should be able to see somthing like this in the STDOUT:

```
{'success': [True], 'status': ['OPTIMAL'], 'obj_val': [66.0], 'solution': [[6.000000000000004, 2.9999999999999987]]}
```


## 6. Alternative: Start the service with Docker

Alternatively, Docker can be used to create segregated environments for running all the services in different containers in a production environment. Use `server.dockerfile` to create container for gateway server service.

Docker environment is required. To install Docker, see [Docker install](https://docs.docker.com/engine/install/)

```bash
# In project directory:
docker build -t gateway-server -f server.dockerfile .
# Start docker, with network synced with the host.
docker run -d --net=host gateway-server
```

Use `py_engine.dockerfile` to create container for Python engine services.

```bash
# In project directory:
docker build -t py-engine-server -f py_engine.dockerfile .
# Start docker, with network synced with the host.
docker run -d --net=host py-engine-server
```

Use `julia_engine.dockerfile` to create container for Julia engine services.

```bash
# In project directory:
docker build -t julia-engine-server -f julia_engine.dockerfile .
# Start docker, with network synced with the host.
docker run -d --net=host julia-engine-server
```

The `compose.yaml` can also be used to start all services together in a single machine.

```bash
  docker-compose -f compose.yaml up
```

## More Information

### Configure service ports

See `config.yaml` for service ip/port configurations.

If ports are changed, remember to change the Dockerfiles respectively to ensure the right ports are opened.



### Scripts in ./scripts folder

The `envSetup.sh` script can be used to install dependencies on a Linux(Debian) system, and other scripts starts different services. The `startAll.sh` runs all the services on local machine.


### Extending the code

See [Contributing.md](contributing.md).
