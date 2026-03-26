function solverOK = changeCobraSolverOptArrow(solverConfig, problemType)
% changeCobraSolverOptArrow COBRA-style OptArrow solver selector.
%
% Supports:
%   changeCobraSolverOptArrow(struct(...), 'LP')
%   changeCobraSolverOptArrow('optarrow', 'LP')

if nargin < 2 || isempty(problemType)
    problemType = 'LP';
end

problemType = upper(problemType);

if isstruct(solverConfig)
    cfg = optarrow.setOptArrowConfig(solverConfig);
elseif ischar(solverConfig) || isstring(solverConfig)
    solverName = char(solverConfig);
    if ~strcmpi(solverName, 'optarrow')
        error('For this adapter, solver name must be ''optarrow'' or a config struct.');
    end
    cfg = optarrow.getOptArrowConfig();
else
    error('solverConfig must be a struct or ''optarrow''.');
end

global CBT_LP_SOLVER CBT_QP_SOLVER CBT_MILP_SOLVER CBT_MIQP_SOLVER

switch problemType
    case 'LP'
        CBT_LP_SOLVER = 'optarrow';
    case 'QP'
        CBT_QP_SOLVER = 'optarrow';
    case 'MILP'
        CBT_MILP_SOLVER = 'optarrow';
    case 'MIQP'
        CBT_MIQP_SOLVER = 'optarrow';
    otherwise
        error('Unsupported problemType: %s', problemType);
end

solverOK = strcmpi(cfg.name, 'optarrow');
end
