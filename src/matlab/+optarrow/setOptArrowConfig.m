function cfg = setOptArrowConfig(cfg)
% setOptArrowConfig Set global OptArrow MATLAB adapter configuration.

global OPTARROW_CONFIG

if nargin < 1 || ~isstruct(cfg)
    error('setOptArrowConfig expects a struct input.');
end

defaults = struct( ...
    'name', 'optarrow', ...
    'engine', 'python', ...
    'backendSolver', 'HiGHS', ...
    'backendSolverType', 'LP', ...
    'backendOptions', struct(), ...
    'endpoint', 'http://127.0.0.1:8000/compute', ...
    'timeoutSec', 120, ...
    'transport', 'arrow');

fields = fieldnames(defaults);
for i = 1:numel(fields)
    fieldName = fields{i};
    if ~isfield(cfg, fieldName) || isempty(cfg.(fieldName))
        cfg.(fieldName) = defaults.(fieldName);
    end
end

if ~strcmpi(cfg.transport, 'arrow')
    error('Only Arrow transport is supported in this interface.');
end

OPTARROW_CONFIG = cfg;
end
