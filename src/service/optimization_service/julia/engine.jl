include("api/socket_server.jl")
using Logging
global_logger(ConsoleLogger(stderr, Logging.Info)) # Set global logger to log info to stderr

# This is the entry point for the Julia optimization service.
# It starts the TCP server.
try
    host = ARGS[1]
    port = parse(Int, ARGS[2])
    SocketServer.start_server(host, port)
catch e
    @error "Failed to start server: $e"
end
