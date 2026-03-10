"""
Run script to start the Python engine server for optimization tasks.
"""
import multiprocessing, threading
import logging
import sys
import yaml
from service.optimization_service.python.pyomo.controller.arrow_rpc_server import grpc_serve_addr
from utils.load_config import load_config_section
from utils.watcher import *
# Run all servers in multiprocessing

class PyEngineServer():
    """
    PyEngineServer class to run the Python optimization engine server.
    This class is responsible for configuring the Python server, setting up logging,
    and running the Python engine in a separate process.
    It reads configuration from a YAML file to determine the IP address and port for the Python
    server.
    """
    def __init__(self, config_path = "config.yaml"):
        cfg = load_config_section(config_path, "grpc")
        self.ip = cfg["ip"]
        self.port = int(cfg["port"])

    def setup_custom_logger(self, name):
        """Set custom logger for a subprocess

        Args:
            name (str): Name of the logger

        Returns:
            Logger: Logger object
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(f'%(levelname)s:     %(message)s')
        handler.setFormatter(formatter)
        # Avoid adding multiple handlers if re-run
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        return self.logger


    def run_grpc_server(self):
        """Start Python engine service
        """
        logger = self.setup_custom_logger(f"worker_grpc")
        logger.info("Starting worker on gRPC server")
        grpc_serve_addr(self.ip, self.port, logger)

    def start_engine_services(self) -> None:
        """Start Python engine service in a subprocess
        """
        grpc_thread = multiprocessing.Process(target=self.run_grpc_server, daemon=True)
        grpc_thread.start()
        
        processes_dict = {
            "py": (grpc_thread, self.run_grpc_server, True),
        }
        monitor_thread = threading.Thread(target=monitor_processes, daemon=True, args=(processes_dict,))
        monitor_thread.start()
        monitor_thread.join()
        
        grpc_thread.join()

# Run script to start engine service
if __name__ == "__main__":
    server = PyEngineServer()
    server.start_engine_services()
