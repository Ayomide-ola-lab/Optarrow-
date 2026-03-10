"""
Run script to start the HTTP gateway server and engine servers together for debugging and testing.
"""
import logging
import multiprocessing, threading
from run_server import GatewayServer
from run_julia_engine import JuliaEngineServer
from run_py_engine import PyEngineServer
from utils.watcher import *

# Run script to start http gateway server and engine server together, for debugging and testing
if __name__ == "__main__":
    global is_end
    is_end = False
    logger = logging.getLogger(__name__)
    server = GatewayServer()
    py_engine_server = PyEngineServer()
    jl_engine_server = JuliaEngineServer()
    jl_thread = multiprocessing.Process(target=jl_engine_server.run_julia_server_with_restart, daemon=True)
    grpc_thread = multiprocessing.Process(target=py_engine_server.run_grpc_server, daemon=True)
    server_thread = multiprocessing.Process(target=server.run_server, daemon=False)
    processes_dict = {
        "jl": (jl_thread, jl_engine_server.run_julia_server_with_restart, True),
        "py": (grpc_thread, py_engine_server.run_grpc_server, True),
        "api": (server_thread, server.run_server, False)
    }
    monitor_thread = threading.Thread(target=monitor_processes, daemon=True, args=(processes_dict,))
    server_thread.start()
    grpc_thread.start()
    jl_thread.start()
    # Start with monitor
    monitor_thread.start()
    while True:
        try:
            for name, item in list(processes_dict.items()):
                proc, worker, is_daemon = item
                proc.join()
        except KeyboardInterrupt:
            is_end = True
            
            logger.info("[Main] Interrupted. Terminating processes...")
            for p in processes_dict.values():
                p[0].terminate()
            monitor_thread.join()