"""
Run script to start the Julia engine server for optimization tasks.
"""
import multiprocessing, threading
import logging
import sys
import time
import subprocess
from utils.load_config import load_config_section
from utils.watcher import *
# Run all servers in multiprocessing
import socket
import pyarrow as pa

class JuliaEngineServer():
    """
    JuliaEngineServer class to run the Julia optimization engine server.
    This class is responsible for configuring the Julia server, setting up logging,
    and running the Julia engine in a separate process.
    It reads configuration from a YAML file to determine the IP address and port for the Julia server
    """
    def __init__(self, config_path = "config.yaml"):
        cfg = load_config_section(config_path, "julia")
        self.ip = cfg["ip"]
        self.port = int(cfg["port"])

    def setup_custom_logger(self, name:str):
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

    def run_julia_server_with_restart(self, max_retries=999):
        self.setup_custom_logger("JuliaEngine")
        retries = 0
        
        
        while retries < max_retries:
            self.logger.info(f"Start Julia Engine Service (Attempt {retries + 1})...")
            cmd = [
                "julia",
                "--project=src/service/optimization_service/julia",
                "src/service/optimization_service/julia/engine.jl",
                self.ip,
                str(self.port)
            ]
            try:
                proc = subprocess.Popen(cmd)  # start Julia process 
                time.sleep(5)  # Give it some time to start

                # Wait for the process to warm up
                connected = False
                for _ in range(10):
                    if self._warm_up_connection(timeout=30):
                        connected = True
                        self.logger.info(f"Julia Engine is ready on {self.ip}:{self.port}.")
                        break
                    time.sleep(1)

                if not connected:
                    # If not warm up within 300 seconds, kill the process
                    self.logger.error("Julia Engine did not respond in time, killing process...")
                    proc.kill()
                    retries += 1
                    time.sleep(3)
                    continue

                # Wait for the Julia process to complete
                proc.wait()
                self.logger.info("Julia Engine Service exited normally")
                break

            except Exception as e:
                self.logger.error(f"Julia Engine Service crashed: {e}, restarting in 3 seconds...")
                retries += 1
                time.sleep(3)


    def _warm_up_connection(self, timeout=1) -> bool:
        try:
            with socket.create_connection((self.ip, self.port), timeout=timeout) as s:
                message_table = pa.table({
                    "A": pa.StructArray.from_arrays(
                        [
                            pa.array([[0, 1]]),
                            pa.array([[0, 0]]),
                            pa.array([[1.0, 2.0]])
                        ],
                        names=["col", "row", "val"]
                    ),
                    "b": [[1.0]],
                    "c": [[1.0, 1.0]],
                    "lb": [[0.0, 0.0]],
                    "ub": [[20, 20]],
                    "osense": ["min"],
                    "csense": [["E"]],

                    "solver": pa.StructArray.from_arrays(
                        [
                            pa.array(["HiGHS"]),
                            pa.array(["LP"]),
                        ],
                        names=["solver_name", "solver_type"]
                    ),
                })
                # Serialize to Arrow stream
                sink = pa.BufferOutputStream()
                with pa.ipc.new_stream(sink, message_table.schema) as writer:
                    writer.write(message_table)
                ipc_bytes = sink.getvalue()

                s.sendall(len(ipc_bytes).to_bytes(4, byteorder='little', signed=True))
                s.sendall(ipc_bytes)
                # Receive the response from the Julia service
                response = s.recv(4)
                length_bytes = response[:4]
                result_length = int.from_bytes(length_bytes, byteorder='little', signed=True)

                #  read the actual response data
                response_data = s.recv(result_length)
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect Julia Engine: {e}")
            return False
        
    def start_engine_services(self) -> None:
        """Run julia service in a separate process
        """
        p = multiprocessing.Process(target=self.run_julia_server_with_restart, daemon=True)
        p.start()
        
        processes_dict = {
            "jl": (p, self.run_julia_server_with_restart, True),
        }
        monitor_thread = threading.Thread(target=monitor_processes, daemon=True, args=(processes_dict,))
        monitor_thread.start()
        monitor_thread.join()
        p.join()

# Run script to start engine service
if __name__ == "__main__":
    server = JuliaEngineServer()
    server.start_engine_services()
