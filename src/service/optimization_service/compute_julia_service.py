"""
JuliaComputeService: A service for computing models using Julia via IPC
"""
import socket
import pyarrow as pa
from service.optimization_service.base_opt_service import BaseOptService
from arrow_table_dict_conversion import dict_to_pa_table
from utils.load_config import load_config_section

class JuliaComputeService(BaseOptService):
    """
    JuliaComputeService: A service for computing models using Julia via IPC
    This service connects to a Julia process over a socket and sends model data
    for computation. It expects the Julia service to be running and listening on
    a specified IP and port.
    It uses PyArrow for serialization and deserialization of model data.
    """
    def __init__(self, config_path = "config.yaml", ip = None, port = None):
        cfg = load_config_section(config_path, "julia")
        self.ip = ip if ip is not None else cfg["ip"]
        self.port = int(port) if port is not None else int(cfg["port"])

    def compute(self, model = None, solver = None, model_name = None, time_limit=300) -> pa.Table:
        """Compute method implementation based on Socket and Julia service

        Args:
            model (dict): The model to compute
            solver (dict): The solver configuration to use
            model_name (str, optional): Optional name for the model. Defaults to None.
        Returns:
            pa.Table: Result of the computation as a PyArrow Table
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.ip, self.port))

                message_dict = model.to_pydict()
                message_dict["solver"] = solver.to_pydict()
                message_dict["time_limit"] = time_limit
                message_table = dict_to_pa_table(message_dict)

                # turn the table to IPC bytes
                sink = pa.BufferOutputStream()
                with pa.ipc.new_stream(sink, message_table.schema) as writer:
                    writer.write(message_table)
                # framing: send the length of the message first
                client_socket.sendall(len(sink.getvalue()).to_bytes(4, byteorder='little', signed=True))
                client_socket.sendall(sink.getvalue())

                # Receive the response from the Julia service
                response = client_socket.recv(4)

                # first 4 bytes are the length of the response
                length_bytes = response[:4]
                result_length = int.from_bytes(length_bytes, byteorder='little', signed=True)

                #  read the actual response data
                response_data = self._recv_all(client_socket, result_length)
                reader = pa.ipc.open_stream(response_data)
                response_table = reader.read_all()

                return response_table
            except socket.error as e:
                # for any other socket errors, close the socket and raise a ConnectionError
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
                raise ConnectionError(f"Failed to connect to Julia service at {self.ip}:{self.port}. Error: {e}") from e

    def _recv_all(self, sock, total_bytes: int) -> bytes:
        data = bytearray()
        while len(data) < total_bytes:
            chunk = sock.recv(min(65536, total_bytes - len(data)))  # read 64kB at a time
            if not chunk:
                raise ConnectionError("Socket closed before receiving all data")
            data.extend(chunk)
        return bytes(data)