function result = compute(payload, varargin)
% compute Submit a generic OptArrow request using Arrow IPC.

if nargin < 1 || ~isstruct(payload)
    error('compute expects payload as a struct.');
end

cfg = optarrow.getOptArrowConfig();

if nargin >= 2 && isstruct(varargin{1})
    opts = varargin{1};
    if isfield(opts, 'endpoint')
        cfg.endpoint = opts.endpoint;
    end
    if isfield(opts, 'timeoutSec')
        cfg.timeoutSec = opts.timeoutSec;
    end
end

if ~isfield(payload, 'engine') || isempty(payload.engine)
    payload.engine = cfg.engine;
end

if ~isfield(payload, 'solver') || isempty(payload.solver)
    payload.solver = struct( ...
        'solver_name', cfg.backendSolver, ...
        'solver_type', cfg.backendSolverType, ...
        'solver_params', cfg.backendOptions);
end

if ~isfield(payload, 'model_name') || isempty(payload.model_name)
    payload.model_name = 'optarrow_model';
end

result = localCallPythonBridge(payload, cfg.endpoint, cfg.timeoutSec);
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
