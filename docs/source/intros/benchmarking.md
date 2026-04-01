# Benchmark testing

The repository now includes a curated reference corpus under
`tests/fixtures/reference/`.

- `tests/fixtures/reference/fixtures/` contains active OptArrow-ready LP/QP
  reference cases with expected outcomes.
- `tests/fixtures/reference/raw/` stores vendored benchmark source files from
  external libraries that are not yet executable in the harness.
- `tests/reference_benchmarks/` contains the pytest-based benchmark checks used
  for direct solver validation and gateway-level validation.

Run the reference benchmark suite with:

```bash
pytest tests/reference_benchmarks -q
```

If the local environment does not have the required optional solver stack or a
gateway service running, the relevant tests will be skipped instead of failing
at import time.

To add a new benchmark:

1. Add the normalized fixture JSON under `tests/fixtures/reference/fixtures/`.
2. Register it in `tests/fixtures/reference/catalog.json`.
3. Vendor any raw source file under `tests/fixtures/reference/raw/` when useful for
   provenance or future parser work.
4. Include the expected status/objective, and solution only when it is stable.

In order to do benchmark testing, use the source code from `benchmark` branch, this includes extra benchmark outputs such as compute time, RAM usage and CPU percentage output. 

The unit tests in that branch can write .csv outputs to list the benchmark test results, and they are organized into different .csv files based on engines and problem types.

Use this to switch branch and execute test:

```bash

git checkout benchmark
poetry run pytest -s

```

You can find the benchmark output files under the project root directory.
