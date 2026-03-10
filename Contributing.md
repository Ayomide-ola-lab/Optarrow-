# Contributing to Arrow Gateway Engine

Thank you for your interest in contributing! This guide will help you get started.

## Project Structure

- `./src`: Main source code.
- `./tests`: Test suite for the project.

## Getting Started

1. **Fork the repository** and clone your fork.
2. **Install dependencies** as required by the project. You may use the `./scripts/envSetup.sh` to install dependencies quickly in a Linux(Debian) system. `Poetry` is used to manage python dependencies, but Julia dependencies need to be installed manually. Run `julia --project=./src/service/optimization_service/julia -e "import Pkg; Pkg.instantiate()"` to install julia dependencies.
3. **Create a new branch** for your feature or bugfix.

    ```bash
    git checkout -b feature/your-feature-name
    ```

## Making Changes

- Place all source code changes in the `src` directory.
- Add or update tests in the `tests` directory.
- Add or update documentations in the `docs` directory.
- Ensure your code follows the project's style and linting rules.

## Running Tests

Run the test suite to verify your changes:

```bash
poetry run pytest
```

Add `-s` to see STDOUT output from the tests.

## Submitting Changes

1. Commit your changes with clear messages.
2. Push your branch to your fork.
3. Open a Pull Request against the main repository.

## Code Review

- Address any feedback from reviewers.
- Ensure all tests pass before merging.

## Questions?

Open an issue if you need help or clarification.

---
Thank you for contributing!
