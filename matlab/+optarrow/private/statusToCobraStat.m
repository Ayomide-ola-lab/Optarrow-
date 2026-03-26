function stat = statusToCobraStat(statusText, success)
% statusToCobraStat Map OptArrow status values to COBRA standardized stat.
%
% COBRA conventions:
%   1 optimal, 0 infeasible, 2 unbounded, -1 unknown/error

if nargin < 2
    success = false;
end

if isempty(statusText)
    statusText = 'unknown';
end

statusText = lower(string(statusText));

if success && (statusText == "optimal" || statusText == "success")
    stat = 1;
    return;
end

if contains(statusText, "infeasible")
    stat = 0;
    return;
end

if contains(statusText, "unbounded")
    stat = 2;
    return;
end

if success
    stat = 1;
else
    stat = -1;
end
end
