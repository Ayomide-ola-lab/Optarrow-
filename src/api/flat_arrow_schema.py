"""Flat Arrow IPC schema for the OptArrow Gateway interface.

This module defines the typed Arrow schema used by the /cobra/compute endpoint.
The schema is intentionally flat (no nested struct columns) so that it can be
constructed natively in any language with a basic Arrow library — MATLAB,
Python, Julia, R — without requiring struct-array or nested-type support.

Request schema (single-row table, list columns hold the vector data):
    problem_type   utf8                     "LP" | "QP"
    engine         utf8                     "python" | "julia" | ...
    solver_name    utf8                     "HiGHS" | "Gurobi" | ...
    model_name     utf8                     label for logging
    time_limit     float64                  seconds (0.0 → use default 300 s)
    osense         utf8                     "min" | "max"
    A_row          list<int64>              COO row indices, 0-based
    A_col          list<int64>              COO col indices, 0-based
    A_val          list<float64>            COO values
    A_nrows        int64                    number of constraint rows
    A_ncols        int64                    number of variables
    b              list<float64>            RHS vector
    c              list<float64>            objective coefficients
    lb             list<float64>            variable lower bounds
    ub             list<float64>            variable upper bounds
    csense         list<utf8>               ["L","E","G"] per constraint
    Q_row          list<int64>              QP: Hessian COO rows (empty for LP)
    Q_col          list<int64>             QP: Hessian COO cols
    Q_val          list<float64>            QP: Hessian COO values
    param_keys     list<utf8>               solver param names
    param_vals     list<utf8>               solver param values (stringified)

Response schema (single-row table):
    success        bool
    status         utf8
    stat           int64     1=optimal, 0=infeasible, 2=unbounded, -1=error
    obj_val        float64
    solution       list<float64>
    dual           list<float64>
    rcost          list<float64>
    slack          list<float64>
    method         utf8
    time           float64
"""

from __future__ import annotations

from typing import Any

import pyarrow as pa


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

REQUEST_SCHEMA = pa.schema([
    pa.field("problem_type",  pa.utf8()),
    pa.field("engine",        pa.utf8()),
    pa.field("solver_name",   pa.utf8()),
    pa.field("model_name",    pa.utf8()),
    pa.field("time_limit",    pa.float64()),
    pa.field("osense",        pa.utf8()),
    pa.field("A_row",         pa.list_(pa.int64())),
    pa.field("A_col",         pa.list_(pa.int64())),
    pa.field("A_val",         pa.list_(pa.float64())),
    pa.field("A_nrows",       pa.int64()),
    pa.field("A_ncols",       pa.int64()),
    pa.field("b",             pa.list_(pa.float64())),
    pa.field("c",             pa.list_(pa.float64())),
    pa.field("lb",            pa.list_(pa.float64())),
    pa.field("ub",            pa.list_(pa.float64())),
    pa.field("csense",        pa.list_(pa.utf8())),
    pa.field("Q_row",         pa.list_(pa.int64())),
    pa.field("Q_col",         pa.list_(pa.int64())),
    pa.field("Q_val",         pa.list_(pa.float64())),
    pa.field("param_keys",    pa.list_(pa.utf8())),
    pa.field("param_vals",    pa.list_(pa.utf8())),
])

RESPONSE_SCHEMA = pa.schema([
    pa.field("success",  pa.bool_()),
    pa.field("status",   pa.utf8()),
    pa.field("stat",     pa.int64()),
    pa.field("obj_val",  pa.float64()),
    pa.field("solution", pa.list_(pa.float64())),
    pa.field("dual",     pa.list_(pa.float64())),
    pa.field("rcost",    pa.list_(pa.float64())),
    pa.field("slack",    pa.list_(pa.float64())),
    pa.field("method",   pa.utf8()),
    pa.field("time",     pa.float64()),
])


# ---------------------------------------------------------------------------
# Deserialise: flat Arrow table → model dict for the existing controller
# ---------------------------------------------------------------------------

def decode_request(table: pa.Table) -> dict[str, Any]:
    """Convert a /cobra/compute Arrow request table to a controller payload."""

    def col(name: str):
        return table.column(name)[0].as_py()

    problem_type = (col("problem_type") or "LP").upper()
    engine       = col("engine") or "python"
    solver_name  = col("solver_name") or ""
    model_name   = col("model_name") or "cobra_model"
    time_limit   = float(col("time_limit") or 0) or 300.0
    osense       = (col("osense") or "min").lower()

    A_row   = [int(x) for x in (col("A_row")  or [])]
    A_col   = [int(x) for x in (col("A_col")  or [])]
    A_val   = [float(x) for x in (col("A_val") or [])]
    A_nrows = int(col("A_nrows") or 0)
    A_ncols = int(col("A_ncols") or 0)
    b       = [float(x) for x in (col("b")   or [])]
    c       = [float(x) for x in (col("c")   or [])]
    lb      = [float(x) for x in (col("lb")  or [])]
    ub      = [float(x) for x in (col("ub")  or [])]
    csense  = [str(x) for x in (col("csense") or [])]

    Q_row = [int(x)   for x in (col("Q_row") or [])]
    Q_col = [int(x)   for x in (col("Q_col") or [])]
    Q_val = [float(x) for x in (col("Q_val") or [])]

    # Reconstruct solver params from parallel key/value lists
    param_keys = list(col("param_keys") or [])
    param_vals = list(col("param_vals") or [])
    solver_params: dict[str, Any] = {}
    for k, v in zip(param_keys, param_vals):
        # Try to convert to number; fall back to string
        try:
            solver_params[k] = int(v)
        except (ValueError, TypeError):
            try:
                solver_params[k] = float(v)
            except (ValueError, TypeError):
                solver_params[k] = v

    # Build the model dict in the format the existing Gateway controller expects
    model: dict[str, Any] = {
        "A": {"row": A_row, "col": A_col, "val": A_val},
        "b": b,
        "c": c,
        "lb": lb if lb else [0.0] * A_ncols,
        "ub": ub if ub else [1e30] * A_ncols,
        "osense": osense,
        "csense": csense if csense else ["E"] * A_nrows,
    }

    if problem_type == "QP":
        model["Q"] = {"row": Q_row, "col": Q_col, "val": Q_val}
        # Remove A/b from model dict if there are no constraints
        if not A_row:
            del model["A"]
            del model["b"]
            del model["csense"]

    return {
        "model":      model,
        "model_name": model_name,
        "engine":     engine,
        "time_limit": time_limit,
        "solver": {
            "solver_name":   solver_name,
            "solver_type":   problem_type,
            "solver_params": solver_params,
        },
    }


# ---------------------------------------------------------------------------
# Serialise: raw solver result → flat Arrow response table
# ---------------------------------------------------------------------------

def _map_stat(status: str | None) -> int:
    s = (status or "").strip().lower()
    if s in {"optimal", "locallyoptimal"}:
        return 1
    if s == "infeasible":
        return 0
    if s == "unbounded":
        return 2
    return -1


def encode_response(raw: dict[str, Any], elapsed: float = 0.0) -> pa.Table:
    """Convert a raw solver result dict to a flat Arrow response table."""
    success = bool(raw.get("success", False))
    status  = str(raw.get("status", "error"))
    stat    = _map_stat(status)
    obj_val = float(raw["obj_val"]) if raw.get("obj_val") is not None else float("nan")

    solution = [float(x) for x in (raw.get("solution") or [])]
    dual     = [float(x) for x in (raw.get("dual")     or [])]
    rcost    = [float(x) for x in (raw.get("rcost")    or [])]
    slack    = [float(x) for x in (raw.get("slack")    or [])]
    method   = str(raw.get("lpmethod") or raw.get("qpmethod") or "optarrow")
    t        = float(raw.get("time", elapsed))

    return pa.table(
        {
            "success":  pa.array([success],  type=pa.bool_()),
            "status":   pa.array([status],   type=pa.utf8()),
            "stat":     pa.array([stat],      type=pa.int64()),
            "obj_val":  pa.array([obj_val],  type=pa.float64()),
            "solution": pa.array([solution], type=pa.list_(pa.float64())),
            "dual":     pa.array([dual],     type=pa.list_(pa.float64())),
            "rcost":    pa.array([rcost],    type=pa.list_(pa.float64())),
            "slack":    pa.array([slack],    type=pa.list_(pa.float64())),
            "method":   pa.array([method],   type=pa.utf8()),
            "time":     pa.array([t],         type=pa.float64()),
        },
        schema=RESPONSE_SCHEMA,
    )


def encode_error(message: str) -> pa.Table:
    """Build a failure response table."""
    return encode_response({"success": False, "status": message}, elapsed=0.0)
