# OptimizationServer (Python)

This project implements a lightweight gRPC-based optimization server. It receives optimization problems (e.g. LP, QP) encoded in Arrow IPC format, solves them using Pyomo in Python and solver backends, and returns the result. The server listens for incoming gRPC connections and sends optimization results serialized in Arrow IPC format.

## 📁 Project Structure
```
python/pyomo
├── problems/ # concrete problem classes (extends BaseProblem class)
│ ├── lp_problem.py
│ └── qp_problem.py
│
├── controller/ # Optimization gRPC service endpoint
│ └── arrow_rpc_server.py
│
├── service/ # Business logic and factories
│ └── opt_solver.py # Core solver service wrapper class
│
├── objects/ # Reusable factories and class definitions
│ ├── base_problem.py # base problems class
│ ├── problem_factory.py # factory class for creating problem objects
│ ├── solver_factory.py # factory class for creating solver objects
│ └── solver.py # base solver class
│
```



## 🚀 Getting Started

### 1.  Install dependencies

On project root directory, run:

```poetry install --no-root```

This installs python dependencies using poetry

### 2. Install solvers

Most of the open-source solvers are installed with the python dependencies, however there are several exceptions, which require the solver to be manually installed, or require license:

- HiGHS (only for QP, [installation guide](https://ergo-code.github.io/HiGHS/dev/interfaces/cpp/))
- Gurobi (requires license)
- Ipopt ([installation guide](https://coin-or.github.io/Ipopt/INSTALL.html))

### 3. Start the server 

using script:

```./scripts/startPyEngine.sh```

You should see:

```INFO:     Server running at grpc://0.0.0.0:8101```

Alternatively, use script:

```./scripts/startAll.sh```

To start all services, including FastAPI gateway and Julia engine.