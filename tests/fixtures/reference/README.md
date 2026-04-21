# Reference Benchmark Corpus

This directory contains repository-local reference problems used to validate
OptArrow behavior against stable expected outcomes.

The corpus is split into two layers:

- `fixtures/`: normalized OptArrow-ready JSON fixtures that can be executed by
  the current test suite.
- `raw/`: vendored benchmark source files from external libraries. These are
  stored with source metadata so we can activate them later as parser and
  problem-class support improves.

## Goals

- Keep a small, stable set of correctness references in-repo.
- Make every active case traceable to a source or benchmark family.
- Support future CI reporting for passed, skipped, and failed reference cases.

## Layout

- `catalog.json`: master manifest of all reference entries.
- `fixtures/*.json`: active OptArrow-ready benchmark cases.
- `raw/netlib/*`: vendored Netlib LP source files.
- `raw/qplib/*`: vendored QPLIB source files.

## Fixture Schema

Each active fixture stores:

- `id`: unique benchmark identifier
- `suite`: benchmark family
- `source`: provenance metadata
- `model_type`: `LP` or `QP`
- `supported_engines`: engines expected to solve the case today
- `solver`: default solver configuration for tests
- `payload`: OptArrow model payload
- `expected`: reference status/objective/solution expectations

## Current Policy

- Active fixtures must be small enough for regular test execution.
- Objective values are the primary correctness signal.
- Solution vectors are checked only when the fixture declares a stable
  reference solution.
- The active set should prefer official benchmark families such as Netlib LP or
  QPLIB over project-local toy models.
- Heavier official candidates can still be vendored in `raw/` first when they
  are valuable references but not yet suitable for every-PR execution.
- Vendored raw benchmark files may be cataloged before they are executable.
