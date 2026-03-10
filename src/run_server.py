"""
Run the FastAPI server for the HTTP gateway
"""
import multiprocessing, threading
import sys
import logging
import uvicorn
from utils.load_config import load_config_section
from utils.watcher import *
# Run all servers in multiprocessing

class GatewayServer():
    """
    Class to run the FastAPI server for the HTTP gateway
    """
    def __init__(self, config_path="config.yaml"):
        cfg = load_config_section(config_path, "http")
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

    def run_server(self):
        """Start FastAPI server via uvicorn
        """
        self.logger = self.setup_custom_logger(f"worker_fastAPI")
        self.logger.info("Starting worker on FastAPI")
        uvicorn.run("api.routers:app",
                    host=self.ip,
                    port=self.port,
                    log_level="info",
                    access_log=True)

    def run_server_multiprocessing(self):
        """Start FastAPI server in a subprocess
        """
        server_thread = multiprocessing.Process(target=self.run_server, daemon=False)
        server_thread.start()
        
        processes_dict = {
            "py": (server_thread, self.run_server, True),
        }
        monitor_thread = threading.Thread(target=monitor_processes, daemon=True, args=(processes_dict,))
        monitor_thread.start()
        monitor_thread.join()
        
        server_thread.join()

# Run script to start http gateway server
if __name__ == "__main__":
    server = GatewayServer()
    server.run_server()
