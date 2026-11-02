# Local quality gates. Temporary files stay in the caller's scratch directory.
$ErrorActionPreference = "Stop"
if (-not $env:IDCHECK_SCRATCH) { throw "Set IDCHECK_SCRATCH to a disposable directory." }
New-Item -ItemType Directory -Force $env:IDCHECK_SCRATCH | Out-Null
$env:TEMP = (Resolve-Path $env:IDCHECK_SCRATCH).Path
$env:TMP = $env:TEMP
python -m ruff format --check .
if ($LASTEXITCODE) { exit $LASTEXITCODE }
python -m ruff check .
if ($LASTEXITCODE) { exit $LASTEXITCODE }
python -m mypy --strict src tests
if ($LASTEXITCODE) { exit $LASTEXITCODE }
python -m pytest --basetemp (Join-Path $env:IDCHECK_SCRATCH "pytest")
exit $LASTEXITCODE
