# Contributing

Thanks for taking the time. This project keeps a small, predictable shape.

## Setup

```
pip install -r requirements-dev.txt
```

## Before you open a pull request

- Keep public API in `src/idcheck/__init__.py`; internals live in `_`-prefixed modules.
- Add a test for the behaviour you change. Unit tests use supplied values and streams.
  Integration and packaging tests use the real filesystem: they build wheel and sdist
  archives, create a virtual environment, install published `idcheck==0.2.0`, and
  upgrade it to the built wheel. Package-index access is required to obtain the
  published release and isolated build requirements unless provisioned in advance.
- Set `IDCHECK_SCRATCH` to a writable, disposable directory, then run
  `scripts/check.ps1` (format, lint, types, tests) and make sure it passes. The script
  directs `TEMP`, `TMP` and pytest's base directory there. Use a dedicated directory:
  pytest clears its own base directory on subsequent runs.
- One logical change per commit, imperative subject line.

Open an issue first if the change is large or shifts the public API.
