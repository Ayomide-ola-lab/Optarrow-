from service.optimization_service.python.pyomo.objects.base_problem import BaseProblem
from service.optimization_service.python.pyomo.problems.lp_problem import LPProblem
from service.optimization_service.python.pyomo.problems.qp_problem import QPProblem


class ProblemFactory():
    """Factory class for different problems
    When adding new problem class, also modify the constructor here
    """
    def __init__(self, type:str, model:dict):
        if type.upper() == "LP":
            self.problem = LPProblem(model=model)
        elif type.upper() == "QP":
            self.problem = QPProblem(model=model)
        pass