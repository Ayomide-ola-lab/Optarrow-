# OptArrow Architecture

This document describes the current implemented architecture of OptArrow and
the planned evolution path for iterative optimization workloads.

It reflects the repository state as of April 21, 2026.

## Purpose

OptArrow is a cross-language optimization service intended to let clients send
optimization models once per request using Apache Arrow data structures and
solve them through either a Python or Julia execution path behind one public
API.

Today, the main value proposition is:

- one HTTP entry point for clients
- Arrow IPC as the primary binary transport
- support for both Python and Julia solver backends
- a model abstraction that normalizes LP and QP requests before dispatch

The current design is well suited for one-shot solves and coarse-grained remote
optimization. It is not yet optimized for iterative workflows where each solve
depends on the previous one and only a small part of the model changes between
iterations.

## Current Status

### Summary

OptArrow currently implements a request/response architecture with these
runtime components:

- HTTP gateway built with FastAPI
- controller and factory layer that parses the request and dispatches by engine
- Python engine path using PyArrow Flight and Pyomo-based solving
- Julia engine path using raw TCP sockets and JuMP-based solving
- Arrow-backed LP and QP request models

The implementation is operational for stateless LP and QP solves over both
JSON and Arrow IPC HTTP endpoints.

### What Is Implemented Today

- `POST /computeJSON` accepts JSON, converts it to a PyArrow table, and returns
  JSON.
- `POST /compute` accepts Arrow IPC bytes and returns Arrow IPC bytes.
- The gateway chooses the engine from the request payload: `python` or
  `julia`.
- The model factory currently supports `LP`, `QP`, and solver configuration
  objects.
- The Python engine path stores uploaded request tables in memory inside the
  Flight server, runs the solver, then the gateway drops the dataset.
- The Julia engine path opens a socket connection per request, solves the
  problem, returns the result, and closes the connection.
- Both engine paths reconstruct the optimization problem from the request data
  for each solve.

### Important Architectural Reality

Although the docs page under `docs/source/intros/architecture.md` says the
gateway "manages sessions", the current code does not expose a persistent
session API to clients.

In practice, the current system behaves as stateless request/response:

- the HTTP gateway does not create a session identifier
- the client sends a full model for each solve
- the Python engine stores the request only long enough to solve it
- the gateway explicitly drops the Python-engine dataset after the solve
- the Julia engine processes one socket request at a time and closes the
  connection

That means OptArrow currently optimizes interoperability more than iterative
reuse.

### Current Component Architecture

#### 1. Client Layer

Clients currently interact with OptArrow over HTTP and can choose one of two
payload formats:

- JSON for ease of use and debugging
- Arrow IPC stream for better binary transport and lower serialization
  overhead

The client payload contains:

- `model`
- `model_name`
- `engine`
- `solver`
- optional `time_limit`

For LP and QP requests, the client sends full matrix and vector data with each
call.

#### 2. HTTP Gateway

The FastAPI gateway is the public front door.

Responsibilities:

- parse incoming HTTP payloads
- convert JSON to Arrow tables when needed
- pass normalized Arrow tables to the controller
- convert the result back to JSON or Arrow IPC
- surface validation and runtime errors as HTTP responses

Current endpoints:

- `POST /compute`
- `POST /computeJSON`

This layer is intentionally thin. It does not currently maintain solver state,
session state, or model caches on behalf of a client.

#### 3. Controller and Factories

The controller is the orchestration layer between transport and execution.

Responsibilities:

- read `engine`, `solver`, `model_name`, and `model` from the request
- instantiate the right optimization service through `OptServiceFactory`
- instantiate the right request model through `ModelFactory`
- call the selected engine service
- return either a success record or an error record

Factories in the current code:

- `OptServiceFactory` maps `python` to `GrpcComputeService`
- `OptServiceFactory` maps `julia` to `JuliaComputeService`
- `ModelFactory` maps `LP`, `QP`, and solver config objects to concrete models

#### 4. Model Layer

The request model layer provides typed normalization and sanity checks before a
request is sent to an engine.

Current model types:

- `LPModel`
- `QPModel`
- `SolverModel`

Current capabilities:

- Arrow-based sparse COO matrices
- objective sense handling
- bounds handling
- dimension and shape checks
- solver type validation for LP and QP

Current limits:

- no delta model
- no session-scoped state
- no representation of warm starts, basis snapshots, or partial updates
- no explicit iterative optimization request type

#### 5. Python Engine Path

The Python engine path is:

`HTTP gateway -> controller -> GrpcComputeService -> PyArrow Flight server -> solver`

Implementation characteristics:

- transport between gateway and Python engine uses PyArrow Flight
- uploaded request tables are stored in the Flight server's in-memory table map
- solving is triggered through a Flight ticket
- the gateway currently drops the dataset before and after the solve cycle

Strengths:

- good transport abstraction for binary Arrow payloads
- natural place for future session-backed stateful execution
- already has an in-memory dataset map that could become a real session store

Current limitations:

- request data is treated as ephemeral
- no stable session lifecycle
- no delta patching API
- no warm-start contract exposed to clients

#### 6. Julia Engine Path

The Julia engine path is:

`HTTP gateway -> controller -> JuliaComputeService -> TCP socket -> JuMP solver`

Implementation characteristics:

- transport between gateway and Julia engine uses raw TCP sockets
- Arrow IPC bytes are framed with a 4-byte length prefix
- the Julia engine accepts a client connection, solves the request, returns the
  result, and closes the socket

Strengths:

- simple and direct runtime model
- clear language separation
- no HTTP overhead between gateway and Julia engine

Current limitations:

- per-request connection lifecycle
- no persistent model residency
- no iterative state carried across calls
- no server-side delta application path today

### Request Flow Today

The current solve flow is:

1. Client sends the full optimization request to the HTTP gateway.
2. Gateway converts the payload into a PyArrow table.
3. Controller reads the engine and solver configuration.
4. Controller creates a normalized LP or QP model object.
5. Controller dispatches to the selected engine service.
6. The selected engine reconstructs the optimization problem from the request.
7. The solver runs.
8. The engine returns a result table.
9. Gateway serializes the result back to JSON or Arrow IPC and returns it.

This architecture is simple and robust for independent solves, but it implies
that model transfer, model reconstruction, and solver setup occur again for the
next request.

### Current Strengths

- clean separation between transport, controller, model parsing, and engine
  execution
- language-agnostic client experience through one gateway
- Arrow-friendly data model for sparse optimization problems
- straightforward deployment topology
- good base architecture for coarse-grained remote solving

### Current Gaps

The main current gaps are concentrated around iterative and stateful workloads.

- no client-visible session lifecycle
- no distinction between one-shot solves and iterative solve loops
- full model payload is resent each time
- model reconstruction happens each time
- no delta-only update path
- no basis reuse or warm-start contract
- no sticky worker/session affinity mechanism
- no partial result fetch API

These gaps matter most for workflows such as:

- sequential dependent optimizations
- FVA-like repeated solves
- deletion screens
- parameter sweeps where only bounds or objective coefficients change
- MATLAB-driven loops where the control algorithm lives on the client but the
  solver should keep the loaded problem alive

## Future Architecture Direction

### Two Modes of OptArrow

The recommended long-term architecture is to make OptArrow explicitly support
two execution modes.

#### Mode 1: Stateless Solve Mode

This is the current mode, formalized rather than replaced.

Use when:

- each solve is independent
- the client wants the simplest API
- the request is large but infrequent
- the backend language or solver may vary per call

Contract:

- client sends a full model
- server solves once
- server returns the result
- no assumption of reused state

#### Mode 2: Iterative Session Mode

This is the new mode needed for sequential dependent optimization.

Use when:

- one optimization depends on the previous optimization result
- only a small subset of bounds, RHS values, or objective coefficients changes
- warm-start or solver-state reuse matters
- the client algorithm lives in MATLAB, Python, or another external runtime

Contract:

- client opens a session with a base model
- OptArrow loads the model once and pins the session to a worker
- subsequent requests send deltas rather than the whole model
- the worker applies updates in place
- the worker solves again without reconstructing the full problem
- the client fetches only the result fields it needs

### Proposed Iterative Session Architecture

#### Session Lifecycle

The future iterative API should expose a clear lifecycle.

Recommended operations:

- `open_session`
- `apply_delta`
- `solve`
- `get_result`
- `reset_session`
- `close_session`

Optional later operations:

- `snapshot_session`
- `restore_session`
- `heartbeat`
- `extend_lease`

#### Session Semantics

Each session should own:

- a loaded base model
- engine choice
- solver choice
- solver-native model object
- optional warm-start state or basis information
- session metadata such as creation time, last access time, and TTL

Each session should be bound to one worker process or engine instance so that
loaded solver state is preserved between calls.

#### Delta Model

The most important architectural addition is a delta protocol.

The first version should support non-structural updates only:

- variable lower bounds
- variable upper bounds
- linear objective coefficients
- objective sense
- RHS values
- constraint senses where supported
- solver parameters that can be changed without rebuild

To keep delta payloads small and unambiguous:

- use integer indices after session creation, not symbolic IDs
- allow batched sparse updates
- version each delta against the session state

This should be enough to support most iterative FBA-style and MATLAB-driven
optimization loops without re-uploading the full problem.

#### Structural Changes

Structural edits should be treated separately from simple deltas.

Examples:

- adding variables
- adding constraints
- changing matrix sparsity structure
- switching from LP to QP

Recommended v1 rule:

- if structure changes, either reject the patch or require a controlled
  rebuild/new session

This keeps the first iterative design much simpler and easier to make correct.

#### Result Fetch Strategy

Iterative mode should avoid always returning the full solution.

Recommended result options:

- objective value only
- objective value plus status
- selected primal variable indices
- selected dual variable indices
- full result when explicitly requested

This matters because iterative algorithms often need only one scalar, a small
vector slice, or a convergence metric before deciding the next update.

#### Warm-Start and Basis Reuse

Iterative mode should distinguish between two classes of backend behavior.

##### Warm-start-capable solvers

For solvers such as HiGHS, Gurobi, and CPLEX, the architecture should preserve:

- loaded solver model
- basis or equivalent solver state where supported
- in-place parameter updates

This gives the highest benefit for sequential dependent LP and MILP workloads.

##### Non-warm-start backends

For backends where basis reuse is not meaningful, iterative mode is still
valuable because it avoids:

- reserializing the full model
- rebuilding the full solver problem
- reconnecting and renegotiating runtime state

Even without warm-start, sessioned execution can still reduce overhead
substantially.

#### Transport Design for Iterative Mode

The public API can remain HTTP-first, but the internal transport should become
explicitly session-aware.

A practical architecture is:

- keep HTTP as the public gateway
- keep Arrow IPC as the canonical payload format
- add session-aware endpoints at the gateway
- keep engine-specific state behind the gateway

Possible future endpoints:

- `POST /sessions`
- `POST /sessions/{session_id}/delta`
- `POST /sessions/{session_id}/solve`
- `GET /sessions/{session_id}/result`
- `DELETE /sessions/{session_id}`

For the Python engine specifically, PyArrow Flight could also support a more
native stateful protocol internally.

#### Scheduling and Affinity

Iterative mode will require explicit routing rules.

Requirements:

- a session must remain attached to a specific worker or engine instance
- the gateway must know where a session lives
- requests for a session must be routed back to the same backend

This introduces state management concerns that the current stateless gateway
does not have:

- worker affinity
- session lookup
- capacity management
- cleanup of abandoned sessions

#### Reliability and Cleanup

Stateful execution makes lifecycle management important.

Recommended safeguards:

- time-to-live for inactive sessions
- explicit client close operation
- idle-session reaper
- heartbeat or lease renewal for long-running loops
- safe failure semantics if a worker dies
- optional session snapshots for recovery in long workflows

#### Security and Multi-Tenancy Considerations

If OptArrow evolves into a shared service, session mode will need:

- authenticated session ownership
- per-session resource limits
- solver license accounting where relevant
- quotas on memory, wall time, and concurrent sessions
- auditability of who opened and closed a session

These concerns are minor in a local prototype but important in a remote
clustered deployment.

### Recommended Near-Term Roadmap

#### Phase 1: Document Current Stateless Mode Clearly

- clarify in docs that the current public API is stateless
- remove or qualify wording that suggests client-visible session management
- document exact request and response schemas for LP and QP

#### Phase 2: Introduce Session Primitives

- add `open_session` and `close_session`
- add session IDs and session metadata
- keep one base model resident per session
- route each session to a sticky worker

#### Phase 3: Add Delta-Only Iteration

- add sparse index-based bound/objective/RHS update messages
- add `solve(session_id)` after `apply_delta`
- add selective result retrieval

#### Phase 4: Add Warm-Start Contracts

- expose backend capability flags
- preserve basis state where supported
- define fallback behavior for backends without warm-start support

#### Phase 5: Add Structural Rebuild Support

- allow controlled rebuilds inside a session
- distinguish lightweight delta updates from full structural changes
- preserve the same client session identity across rebuild when possible

## Architectural Recommendation

OptArrow should not replace its current stateless design. It should add a
second, explicit execution mode for iterative optimization.

The architecture target should be:

- stateless mode for simple and independent remote solves
- iterative session mode for dependent sequential optimization

That gives OptArrow a clear, scalable design:

- simple where simplicity is enough
- stateful where performance depends on reuse

## Short Version

Current OptArrow:

- one-shot request/response
- full model per call
- good for interoperability
- not yet optimized for iterative loops

Future OptArrow:

- session-aware
- delta-based updates
- sticky worker affinity
- selective result fetch
- warm-start reuse where the backend supports it

This is the right direction for MATLAB-driven iterative optimization and other
client-controlled sequential workflows.
