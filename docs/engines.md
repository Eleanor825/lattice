# Engine Runtime Notes

Lattice now includes an execution layer for compiling normalized JSONL source records through multiple engines:

- `local`
- `spark`
- `flink`

## What Is Already Verified

### Local engine

Verified in the current environment.

### Spark engine

Verified in local mode with:

- Java available
- `pyspark==3.5.5` installed
- `PYSPARK_PYTHON` and `PYSPARK_DRIVER_PYTHON` pinned to the active interpreter

The repository now supports:

```bash
PYTHONPATH=src python3 -m lattice engine-check
PYTHONPATH=src python3 -m lattice engine-compile --engine spark ...
```

## Flink Status

The Flink execution path is now runnable in the current local environment.

Validated local prerequisites:

- `apache-flink`
- `apache-flink-libraries`
- Java 17
- Python-side runtime dependencies required by PyFlink

The repository also auto-detects a Homebrew `openjdk@17` installation when available and uses it for local Flink execution.

So the current state is:

- the repository is **Flink-compatible at the code level**
- the local environment is **Flink-runnable** when the runtime stack is present
- Flink remains the least stable engine because its dependency chain is heavier than local Python or Spark

## Why This Still Matters

This is not just a documentation distinction.

The codebase now has:

- a shared engine abstraction
- local execution
- Spark execution
- a Flink execution entrypoint and runtime checks

That means the platform is no longer purely conceptual. It already runs locally, through Spark, and through a validated local Flink path.
