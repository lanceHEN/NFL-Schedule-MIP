# NFL Schedule MiP Optimizer

This module provides a small, configurable, mixed-integer-programming-based scheduling framework with a solver-backed optimizer and an example script for generating an NFL schedule.

## Project Structure

```
src/
├── config/
│   ├── config.py        # Central configuration and parameters
│   └── __init__.py
├── example/
│   └── get_schedule.py  # Example script to generate a schedule
├── model/
│   ├── scheduler.py     # Core scheduling and optimization logic
│   └── __init__.py
```

## Overview

- **`config/config.py`**
  - Defines configuration values used by the scheduler (e.g. team strengths, constants, and defaults).
  - Uses structured configuration with post-initialization helpers.

- **`model/scheduler.py`**
  - Implements the scheduling model and optimization routine.
  - Exposes an `NFLScheduler` interface with a `solve(...)` method that runs an optimization solver and returns a schedule.
  - Designed to work with a MIP solver (e.g. Gurobi-style parameters such as gap, time limit, presolve, etc.).

- **`example/get_schedule.py`**
  - Minimal runnable example.
  - Instantiates the scheduler, configures a solver, solves the model, and prints the resulting schedule.

## Usage

Run the example script from the project root:

```bash
python src/example/get_schedule.py
```

This will:
- Load configuration values
- Build the scheduling model
- Solve the optimization problem
- Print the resulting schedule

## Customization
- Adjust model parameters or constants in `config/config.py`
- Modify constraints or objectives in `model/scheduler.py`
- Use `example/get_schedule.py` as a template for downstream analysis or experimentation
  
## Notes
- Solver performance and solution quality depend on time limits and MIP gap settings.