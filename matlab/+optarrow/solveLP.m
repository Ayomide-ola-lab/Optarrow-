function result = solveLP(LPproblem, varargin)
% solveLP Solve a linear problem through OptArrow (general interface).

if nargin < 1 || ~isstruct(LPproblem)
    error('LPproblem must be provided as a struct.');
end

opts = struct();
if nargin >= 2 && isstruct(varargin{1})
    opts = varargin{1};
end

payload = struct();
payload.model = localBuildModelDict(LPproblem);
payload.model_name = 'optarrow_lp_model';

if isfield(opts, 'modelName') && ~isempty(opts.modelName)
    payload.model_name = opts.modelName;
end

if isfield(opts, 'engine') && ~isempty(opts.engine)
    payload.engine = opts.engine;
end

if isfield(opts, 'solver') && ~isempty(opts.solver)
    payload.solver = opts.solver;
end

if isfield(opts, 'time_limit')
    payload.time_limit = opts.time_limit;
end

computeOpts = struct();
if isfield(opts, 'endpoint')
    computeOpts.endpoint = opts.endpoint;
end
if isfield(opts, 'timeoutSec')
    computeOpts.timeoutSec = opts.timeoutSec;
end

if isempty(fieldnames(computeOpts))
    response = optarrow.compute(payload);
else
    response = optarrow.compute(payload, computeOpts);
end

result = response;
end

function model = localBuildModelDict(LPproblem)
if ~isfield(LPproblem, 'A') || ~isfield(LPproblem, 'b') || ~isfield(LPproblem, 'c')
    error('LPproblem must include fields A, b, and c.');
end

A = LPproblem.A;
if ~issparse(A)
    A = sparse(A);
end

[rowIdx, colIdx, val] = find(A);

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

model.csense = localNormalizeCsense(LPproblem, size(A, 1));
model.osense = localNormalizeOsense(LPproblem);
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
        error('Unsupported csense format.');
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
