# Build and upload to PyPI. Run scripts/check.ps1 first.
# Refuse an existing version; the token is read from a secret store, never git.
$ErrorActionPreference = "Stop"
if (git status --porcelain) { throw "Commit or stash changes before publishing." }
if ($LASTEXITCODE) { throw "Cannot read repository status." }
$metadata = Get-Content pyproject.toml -Raw
$version = [regex]::Match($metadata, '(?m)^version = "([^"]+)"').Groups[1].Value
if (-not $version) { throw "Cannot read the release version." }

# Works on both Windows PowerShell 5.1 and pwsh 7 (generic catch, no PS7-only types).
$taken = $true
try {
    Invoke-WebRequest -UseBasicParsing "https://pypi.org/pypi/idcheck/$version/json" | Out-Null
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 404) { $taken = $false } else { throw }
}
if ($taken) { throw "This version of idcheck already exists on PyPI." }

$token = $env:PYPI_TOKEN
if (-not $token -and (Test-Path "C:\secrets\pypi-token.txt")) {
    $token = (Get-Content "C:\secrets\pypi-token.txt" -Raw).Trim()
}
if (-not $token) {
    throw "No PyPI token. Set `$env:PYPI_TOKEN or save it to C:\secrets\pypi-token.txt (never commit it)."
}

$output = Join-Path "dist" ([guid]::NewGuid().ToString())
python -m build --outdir $output
if ($LASTEXITCODE) { throw "Build failed." }
python -m twine check --strict "$output/*"
if ($LASTEXITCODE) { throw "Distribution validation failed." }

$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = $token
try {
    python -m twine upload "$output/*"
    if ($LASTEXITCODE) { throw "Upload failed." }
} finally { Remove-Item Env:\TWINE_PASSWORD -ErrorAction SilentlyContinue }
