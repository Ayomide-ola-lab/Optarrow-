function ok = minimal_optarrow_test(endpoint)
% minimal_optarrow_test Minimal runnable test for the OptArrow MATLAB interface.
%
% USAGE:
%   ok = minimal_optarrow_test()
%   ok = minimal_optarrow_test('http://127.0.0.1:8000/compute')
%
% INPUT:
%   endpoint  char/string (optional), OptArrow /compute endpoint.
%
% OUTPUT:
%   ok        logical scalar, true if request succeeds and basic checks pass.
%
% NOTES:
%   - Start the OptArrow API server before running this test.
%   - This is an integration smoke test (MATLAB -> Python bridge -> OptArrow API).

if nargin < 1 || isempty(endpoint)
    endpoint = 'http://127.0.0.1:8000/compute';
end

% Add src/matlab to MATLAB path (works when called from repo root or anywhere).
thisFile = mfilename('fullpath');
examplesDir = fileparts(thisFile);
repoRoot = fileparts(fileparts(examplesDir)); % .../<repo>
matlabRoot = fullfile(repoRoot, 'src', 'matlab');
addpath(genpath(matlabRoot));

% Configure interface.
optarrow.setOptArrowConfig(struct( ...
    'endpoint', endpoint, ...
    'timeoutSec', 30, ...
    'backendSolver', 'HiGHS', ...
    'backendSolverType', 'LP'));

% Tiny LP:
%   minimize   -x - y
%   subject to x + y <= 1, x <= 1, x >= 0, y >= 0
LP = struct();
LP.A = sparse([1 1; 1 0]);
LP.b = [1; 1];
LP.c = [-1; -1];
LP.lb = [0; 0];
LP.csense = ['L'; 'L'];
LP.osense = 1;   % 1=min

try
    result = optarrow.solveLP(LP);
catch ME
    fprintf(2, 'OptArrow call failed: %s\n', ME.message);
    fprintf(2, 'Check server at %s and Python deps (requests, pyarrow).\n', endpoint);
    ok = false;
    return;
end

assert(isstruct(result), 'Expected result to be a struct.');
assert(~isempty(fieldnames(result)), 'Expected non-empty response from OptArrow.');

if isfield(result, 'http_status')
    assert(result.http_status == 200, 'Expected http_status == 200, got %d.', result.http_status);
end

if isfield(result, 'success')
    assert(logical(result.success), 'Expected success=true. error_message=%s', localGetErrorMessage(result));
end

disp('minimal_optarrow_test: PASS');
disp(result);
ok = true;
end

function msg = localGetErrorMessage(result)
if isfield(result, 'error_message')
    if isstring(result.error_message) || ischar(result.error_message)
        msg = char(result.error_message);
        return;
    end
end
msg = 'n/a';
end
