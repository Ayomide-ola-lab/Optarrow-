"""
Controller for interacting with the service to perform computations.
"""
from typing import Dict
import pyarrow as pa
from model.model_factory import ModelFactory
from service.optimization_service.opt_service_factory import OptServiceFactory
from arrow_table_dict_conversion import dict_to_pa_table, unpack_pa_table_dict


class Controller:
    """
    Controller class interacts with the service layer to execute computations
    using the provided data.
    """
    def __init__(self):
        self.service_factory = OptServiceFactory()
        self.model_factory = ModelFactory()

    def compute_dict(self, payload:dict) -> tuple[bool, dict]:
        """
        Execute computation using provided data, as dict.
        
        For MATLAB use.

        Args:
            payload (dict): input data as a dictionary.
            
        Returns:
            Tuple[bool, pa.RecordBatch]: success flag and result as a PyArrow RecordBatch 
            or error message.
        
        Raises:
            ValueError: if the payload is invalid.
            KeyError: if required columns are missing in the payload.
        """

        try:
            engine:str = str(payload.get("engine"))
            optimization_service = self.service_factory.create_service(engine)
            solver_model = self.model_factory.create_model("solver", payload.get("solver"))
            model_name = payload.get("model_name")
            data_model = self.model_factory.create_model(
                solver_model.solver_type.lower(),
                payload.get("model")
            )
            time_limit = 300
            if "time_limit" in payload and payload.get("time_limit") is not None:
                time_limit = payload.get("time_limit")
            if time_limit is None:
                time_limit = 300
            result = optimization_service.compute(data_model, solver_model, model_name, time_limit)
            result = unpack_pa_table_dict(result)
            if "success" in result and result.get("success"):
                return True, result
            else:
                return False, result
        except Exception as e:
            return False, {
                "error_message": str(e)
            }


    def compute(self, payload) -> tuple[bool, pa.RecordBatch]:
        """
        Execute computation using provided data.

        Args:
            payload (pa.Table): input data as a PyArrow table.
            
        Returns:
            Tuple[bool, pa.RecordBatch]: success flag and result as a PyArrow RecordBatch 
            or error message.
        
        Raises:
            ValueError: if the payload is invalid.
            KeyError: if required columns are missing in the payload.
        """
        try:
            raw_payload = unpack_pa_table_dict(payload)
            success, result = self.compute_dict(raw_payload)
            return success, dict_to_pa_table(result)
        except Exception as e:
            return False, pa.RecordBatch.from_pydict({
                    "error_message": [str(e)]
                })
