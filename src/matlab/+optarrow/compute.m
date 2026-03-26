function result = compute(payload, varargin)
% compute Submit a generic OptArrow request using Arrow IPC transport.
%
% NOTE:
%    'optarrow.compute(...)' is MATLAB package namespace syntax from the
%    '+optarrow' folder, not object-oriented method dispatch.
%
% USAGE:
%
%    result = optarrow.compute(payload)
%    result = optarrow.compute(payload, opts)
%    import optarrow.*
%    result = compute(payload)
%    result = compute(payload, opts)
%
% INPUTS:
%    payload:      struct, request body to send to OptArrow.
%                  Typical fields include:
%                    - model      struct, optimization model dictionary
%                    - model_name char/string, model identifier
%                    - engine     char/string, backend engine
%                    - solver     struct, solver definition and parameters
%                    - time_limit numeric scalar, solve time limit
%
% OPTIONAL INPUTS:
%    opts:         struct with transport overrides.
%                    - endpoint   char/string, API endpoint URL
%                    - timeoutSec numeric scalar, timeout in seconds
%
% OUTPUT:
%    result:       struct, decoded JSON response from the OptArrow server.
%
% EXAMPLE:
%    payload = struct();
%    payload.model = struct('A', struct('row', [0], 'col', [0], 'val', [1]), ...
%                           'b', [1], 'c', [1], 'lb', [0], 'csense', {{'L'}}, ...
%                           'osense', 'min');
%    payload.model_name = 'demo_model';
%    out = optarrow.compute(payload, struct('timeoutSec', 30));

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
