"""
Service class that acts as a gRPC client between gateway and engine gRPC service
"""
import pyarrow as pa
import pyarrow.flight
from arrow_table_dict_conversion import dict_to_pa_table
from service.optimization_service.base_opt_service import BaseOptService
from utils.load_config import load_config_section

class GrpcComputeService(BaseOptService):
    """
    GrpcComputeService: gRPC client for compute service
    This service acts as a client to the gRPC compute service, allowing for
    computation requests to be sent and results to be received.
    It uses PyArrow to serialize and deserialize data for communication.
    It provides methods to compute models using the gRPC service.
    """
    def __init__(self, config_path = "config.yaml", ip = None, port = None):
        cfg = load_config_section(config_path, "grpc")
        self.ip = ip if ip is not None else cfg["ip"]
        self.port = int(port) if port is not None else int(cfg["port"])

    def compute(self, model = None, solver = None, model_name = None, time_limit=300) -> pa.Table:
        """Compute method implementation based on Flight gRPC

        Args:
            model (dict): The model to compute
            solver (dict): The solver configuration to use
            model_name (str, optional): Optional name for the model. Defaults to None.
        Returns:
            pa.Table: Result of the computation as a PyArrow Table
        """
        client = pyarrow.flight.connect(f"grpc://{self.ip}:{self.port}")
        client.as_async()
        # Upload a new dataset
        request_dict = model.to_pydict()
        request_dict["time_limit"] = time_limit
        if "solver" not in request_dict:
            request_dict["solver"] = solver.__dict__
        message_table = dict_to_pa_table(request_dict)

        # Drop the old dataset
        param_str = f"pyomo_params_{model_name}"
        try:
            client.do_action(pa.flight.Action("drop_dataset", param_str.encode('utf-8')))
            upload_descriptor = pa.flight.FlightDescriptor.for_path(param_str)

            writer, reader = client.do_put(upload_descriptor, message_table.schema, options=pa.flight.FlightCallOptions(timeout=120))
            writer.write_table(message_table)
            writer.done_writing()
            _ = reader.read()
            get_param = "do_solver," + param_str + ",pyomo"
            # Compute the model and drop dataset from gRPC server
            result_reader = client.do_get(ticket=pa.flight.Ticket(get_param.encode('utf-8')))
            client.do_action(pa.flight.Action("drop_dataset", param_str.encode('utf-8')))
            res = result_reader.read_all()
            return res
        except Exception as e:
            return pa.Table.from_pydict({"error_message": [str(e)]})
        finally:
            client.close()
