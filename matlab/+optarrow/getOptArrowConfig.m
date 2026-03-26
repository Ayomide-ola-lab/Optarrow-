function cfg = getOptArrowConfig()
% getOptArrowConfig Get global OptArrow MATLAB adapter configuration.

global OPTARROW_CONFIG

if isempty(OPTARROW_CONFIG)
    cfg = optarrow.setOptArrowConfig(struct());
    return;
end

cfg = OPTARROW_CONFIG;
end
