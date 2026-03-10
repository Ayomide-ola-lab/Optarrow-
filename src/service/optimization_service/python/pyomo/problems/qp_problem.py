import logging
from pyomo.environ import *
import numpy as np
from pyomo.opt import SolverStatus, TerminationCondition
import pyarrow.compute as pc
from gethighs import HiGHS
import os
import gc
import time
from utils.pyomo_utils import *
from service.optimization_service.python.pyomo.objects.base_problem import BaseProblem
import shutil
from collections import defaultdict

highs_param_map = {
    -1: "off",
    0: "choose",
    1: "on"
}

logger = logging.getLogger("qp_problem")
class QPProblem(BaseProblem):
    def __init__(self, model=None):
        super().__init__(model)
        A = self.model_params.get("A", None)
        G = self.model_params.get("G", None)
        Q = self.model_params.get("Q", None)
        b = self.model_params.get("b", None)
        c = self.model_params.get("c", None)
        h = self.model_params.get("h", None)
        lb = self.model_params.get("lb", None)
        ub = self.model_params.get("ub", None)
        osense = self.model_params["osense"]
        self.A = {"row":[], "col":[], "val":[]}
        self.G = {"row":[], "col":[], "val":[]}
        self.Q = {"row":[], "col":[], "val":[]}
        # add shape
        if A is not None and isinstance(A, dict) and all(k in A for k in ("row", "col", "val")):
            self.A = sparse_dict_add_shape(A)
        else:
            self.A = sparse_dict_add_shape(self.A)
        if G is not None and isinstance(G, dict) and all(k in G for k in ("row", "col", "val")):
            self.G = sparse_dict_add_shape(G)
        else:
            self.G = sparse_dict_add_shape(self.G)
        if Q is not None and isinstance(Q, dict) and all(k in Q for k in ("row", "col", "val")):
            self.Q = sparse_dict_add_shape(Q)
        else:
            self.Q = sparse_dict_add_shape(self.Q)
        self.b = np.array(b)
        self.c = np.array(c)
        self.h = np.array(h)
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.n = None
        self.meq = None
        self.mieq = None
        if self.c is not None:
            self.n = self.c.shape[0]
        if self.A is not None:
            self.meq = self.A["shape"][0]
        if self.G is not None:
            self.mieq = self.G["shape"][0]
        if osense == 'max':
            self.osense = 1
        elif osense == 'min':
            self.osense = -1
        self.model = None
        self.solution = None
        self.objective_value = None
        self.status = None

    def build(self, solver: SolverConfig):
        model = ConcreteModel()
                
        n = self.c.shape[0]
        model.I = RangeSet(0, n - 1)

        logger.info("Setting x:")
        model.x = Var(model.I, within=Reals)

        # Bounds
        for i in model.I:
            model.x[i].setlb(self.lb[i] if self.lb is not None else None)
            model.x[i].setub(self.ub[i] if self.ub is not None else None)

        logger.info("Setting objectives:")
        # Objective
    
        qsym = defaultdict(float)
        for r, c, v in zip(self.Q["row"], self.Q["col"], self.Q["val"]):
            if r <= c:
                qsym[(r, c)] += v
            else:
                qsym[(c, r)] += v
                
        # Sparse to row based dicts
        def rows_from_triplet(T):
            m = T['shape'][0]
            rows = [list() for _ in range(m)]
            for r, c, v in zip(T['row'], T['col'], T['val']):
                rows[r].append((c, v))
            return rows
        
        Arows = rows_from_triplet(self.A) if self.A and len(self.A['row']) else []
        Grows = rows_from_triplet(self.G) if self.G and len(self.G['row']) else []
            
        quad_expr = sum(v * model.x[i] * model.x[j] for (i, j), v in qsym.items())
        lin_expr = sum(self.c[j] * model.x[j] for j in range(n))
        
        
        model.obj = Objective(expr=0.5 * quad_expr + lin_expr,
                            sense=minimize if self.osense == -1 else maximize)

        # S is now always dense 2D array
        # Setting constraints
        logger.info("Setting constraints:")
        # Ax = b
        if Arows:
            model.eq = ConstraintList()
            for i, terms in enumerate(Arows):
                expr = sum(v * model.x[j] for j, v in terms)
                model.eq.add(expr == self.b[i])

        # Gx <= h
        if Grows:
            model.ineq = ConstraintList()
            for i, terms in enumerate(Grows):
                expr = sum(v * model.x[j] for j, v in terms)
                model.ineq.add(expr <= self.h[i])
                
        self.model = model
        self.solver = solver

    def solve(self, solver_params={}, timeout=300):
        logger.info(f"Timeout: {timeout}")
        # Add /usr/local/lib to LD_LIBRARY_PATH, for ipopt
        os.environ["LD_LIBRARY_PATH"] = "/usr/local/lib:" + os.environ.get("LD_LIBRARY_PATH", "")
        if self.model is None or self.solver is None:
            raise RuntimeError("Model not built or solver not assigned.")
        sol_path = "./sol.sol"
        time_limit = timeout
        if "highs" in self.solver.name.lower(): 
            try:
                # map -1, 0, 1 with "off", "choose", "on" to make it conform with standards of other python engines
                for item in solver_params:
                    if highs_param_map[solver_params[item]] is not None:
                        solver_params[item] = highs_param_map[solver_params[item]]
                opt = HiGHS(solution_file=sol_path, log_file="/dev/null", **solver_params)
                result = opt.solve(self.model, time_limit=time_limit)
            except Exception as e:
                # remove tmp folder
                if os.path.exists("./tmp"):
                    shutil.rmtree("./tmp", )
                raise RuntimeError("HiGHS solve failed, check HiGHS installation (QP requires separate HiGHS installation).")
        else:
            opt = SolverFactory(self.solver.name.lower())
            if solver_params is not None and solver_params != {}:
                for item in solver_params:
                    opt.options[item] = solver_params[item]
            result = opt.solve(self.model, tee=True, timelimit=time_limit)

        if "highs" in self.solver.name.lower(): 
            self.status = str(opt.status)
            if self.status == "Optimal":
                # Get from the sol file
                x = []
                with open(sol_path, "r") as f:
                    lines = f.readlines()
                    section = None
                    is_primal = False
                    for j, line in enumerate(lines):
                        if "# Primal solution values" in line:
                            is_primal = True
                            continue
                        if "Columns" in line:
                            section = "col"
                            continue
                        if "Rows" in line:
                            section = "row"
                            continue
                        if "Dual solution values" in line:
                            is_primal = False
                            continue
                        if is_primal and section == "col":
                            parts = line.strip().split()
                            val = float(parts[-1])
                            x.append(val)
                        
                
                if os.path.exists(sol_path):
                    os.remove(sol_path)
                self.solution = [x]
                self.objective_value = value(opt.objective)
                if self.osense == 1:
                    self.objective_value = -self.objective_value
            else:
                self.solution = self.status
                self.objective_value = None
        else:
            if result.solver.status == SolverStatus.ok:
                logger.info("Solved.")
                self.solution = [value(self.model.x[i]) for i in self.model.I]
                self.objective_value = value(self.model.obj)
                self.status = str(result.solver.termination_condition)
            else:
                self.solution = "Solve did not complete successfully."
                self.objective_value = None
                self.solution = None
                self.status = str(result.solver.termination_condition)
