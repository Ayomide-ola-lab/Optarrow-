from service.optimization_service.python.pyomo.objects.solver import BaseSolver
from service.optimization_service.python.pyomo.service.opt_solver import PyomoSolver

class SolverFactory:
    def __init__(self):
        self._solver_map = {
            "pyomo": PyomoSolver(),
        }
        pass

    def get_solver(self, name:str) -> BaseSolver:
        """Get a certain type of solver

        Args:
            name (str): _description_

        Returns:
            BaseSolver: _description_
        """
        return self._solver_map.get(name)
