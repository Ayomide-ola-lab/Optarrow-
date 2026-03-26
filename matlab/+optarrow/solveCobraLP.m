function solution = solveCobraLP(LPproblem, varargin)
% solveCobraLP Solve LP via OptArrow in COBRA-compatible output shape.

tStart = tic;

if nargin < 1 || ~isstruct(LPproblem)
    error('LPproblem must be a struct.');
end

cfg = optarrow.getOptArrowConfig();

params = struct();
if nargin >= 2 && isstruct(varargin{1})
    params = varargin{1};
end

if isfield(params, 'engine')
    cfg.engine = params.engine;
end
if isfield(params, 'backendSolver')
    cfg.backendSolver = params.backendSolver;
end
if isfield(params, 'backendOptions')
    cfg.backendOptions = params.backendOptions;
end
if isfield(params, 'endpoint')
    cfg.endpoint = params.endpoint;
end
if isfield(params, 'timeoutSec')
    cfg.timeoutSec = params.timeoutSec;
end

modelName = 'optarrow_lp_model';
if isfield(params, 'modelName')
    modelName = params.modelName;
end

model = localBuildModelDict(LPproblem);

payload = struct();
payload.model = model;
payload.model_name = modelName;
payload.engine = cfg.engine;
payload.solver = struct( ...
    'solver_name', cfg.backendSolver, ...
    'solver_type', cfg.backendSolverType, ...
    'solver_params', cfg.backendOptions);

if isfield(params, 'time_limit')
    payload.time_limit = params.time_limit;
end

response = localCallPythonBridge(payload, cfg.endpoint, cfg.timeoutSec);

solution = struct();
solution.solver = 'optarrow';
solution.time = toc(tStart);

if isfield(response, 'solution')
    solution.full = response.solution;
else
    solution.full = [];
end

if isfield(response, 'obj_val')
    solution.obj = response.obj_val;
else
    solution.obj = [];
end

if isfield(response, 'status')
    solution.origStat = response.status;
else
    solution.origStat = 'unknown';
end

if isfield(response, 'http_status')
    solution.httpStatus = response.http_status;
else
    solution.httpStatus = NaN;
end

if isfield(response, 'error_message')
    solution.error_message = response.error_message;
end

success = false;
if isfield(response, 'success')
    success = logical(response.success);
elseif isfield(response, 'http_status')
    success = response.http_status == 200;
end

statusText = 'unknown';
if isfield(response, 'status')
    statusText = char(string(response.status));
end

solution.stat = optarrow.private.statusToCobraStat(statusText, success);
end

function model = localBuildModelDict(LPproblem)
A = LPproblem.A;
if ~issparse(A)
    A = sparse(A);
end
[rowIdx, colIdx, val] = find(A);

csense = localNormalizeCsense(LPproblem, size(A, 1));
osense = localNormalizeOsense(LPproblem);

model = struct();
model.A = struct('row', rowIdx - 1, 'col', colIdx - 1, 'val', val);
model.b = LPproblem.b(:)';
model.c = LPproblem.c(:)';

if isfield(LPproblem, 'lb') && ~isempty(LPproblem.lb)
    model.lb = LPproblem.lb(:)';
else
    model.lb = zeros(1, size(A, 2));
end

if isfield(LPproblem, 'ub') && ~isempty(LPproblem.ub)
    model.ub = LPproblem.ub(:)';
end

model.csense = csense;
model.osense = osense;
end

function csense = localNormalizeCsense(LPproblem, nRows)
if isfield(LPproblem, 'csense') && ~isempty(LPproblem.csense)
    raw = LPproblem.csense;
    if ischar(raw)
        csense = cellstr(raw(:));
    elseif isstring(raw)
        csense = cellstr(raw(:));
    elseif iscell(raw)
        csense = raw;
    else
        error('Unsupported csense type.');
    end
else
    csense = repmat({'E'}, nRows, 1);
end
csense = upper(string(csense));
csense = cellstr(csense);
end

function osense = localNormalizeOsense(LPproblem)
if ~isfield(LPproblem, 'osense') || isempty(LPproblem.osense)
    osense = 'min';
    return;
end

if isnumeric(LPproblem.osense)
    if LPproblem.osense == -1
        osense = 'max';
    else
        osense = 'min';
    end
else
    raw = lower(string(LPproblem.osense));
    if raw == "max"
        osense = 'max';
    else
        osense = 'min';
    end
end
end

function response = localCallPythonBridge(payload, endpoint, timeoutSec)
try
    py.importlib.import_module('json');
    bridge = py.importlib.import_module('optarrow_matlab_bridge');
catch
    bridgePath = fullfile(fileparts(mfilename('fullpath')), '..', 'py');
    if count(py.sys.path, bridgePath) == 0
        insert(py.sys.path, int32(0), bridgePath);
    end
    py.importlib.import_module('json');
    bridge = py.importlib.import_module('optarrow_matlab_bridge');
end

payloadPy = py.json.loads(jsonencode(payload));
respPy = bridge.compute_arrow_ipc(payloadPy, endpoint, int64(timeoutSec));
response = jsondecode(char(py.json.dumps(respPy)));
end
