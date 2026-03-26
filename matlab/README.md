# OptArrow MATLAB Interface (Initial Scaffold)

This folder contains a first MATLAB interface scaffold for OptArrow focused on:

- Arrow IPC transport (`/compute`) only
- COBRA-style solver selection compatibility path
- Scalable sparse model transfer (COO)

## Files

- `+optarrow/setOptArrowConfig.m`: Set global OptArrow runtime config.
- `+optarrow/getOptArrowConfig.m`: Read global OptArrow runtime config.
- `+optarrow/changeCobraSolverOptArrow.m`: Prototype COBRA-style solver switch.
- `+optarrow/solveCobraLP.m`: COBRA-compatible LP wrapper using OptArrow.
- `+optarrow/private/statusToCobraStat.m`: Map OptArrow status to COBRA `stat`.
- `py/optarrow_matlab_bridge.py`: Python bridge for Arrow IPC request/response.

## MATLAB prerequisites

1. MATLAB with Python integration enabled (`pyenv`).
2. Python packages in selected environment:
   - `pyarrow`
   - `requests`

## Quick usage

```matlab
addpath(genpath(fullfile(pwd, 'matlab')));

cfg = struct( ...
    'name', 'optarrow', ...
    'engine', 'python', ...
    'backendSolver', 'HiGHS', ...
    'backendSolverType', 'LP', ...
    'backendOptions', struct(), ...
    'endpoint', 'http://127.0.0.1:8000/compute', ...
    'timeoutSec', 120);

optarrow.changeCobraSolverOptArrow(cfg, 'LP');

LPproblem = struct();
LPproblem.A = sparse([20 10; 10 20; 10 30]);
LPproblem.b = [200; 120; 150];
LPproblem.c = [5; 12];
LPproblem.lb = [0; 0];
LPproblem.ub = [1000; 1000];
LPproblem.csense = ['L'; 'L'; 'L'];
LPproblem.osense = -1;

sol = optarrow.solveCobraLP(LPproblem, struct('modelName', 'matlab_lp'));
disp(sol)
```

## Notes

- This is intentionally Arrow-only to avoid duplicate JSON code paths.
- Intended as a clean starting point for COBRA Toolbox upstream integration.