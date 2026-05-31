$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

pip install -q -r requirements.txt

Write-Host "== sanity: pytest =="
python -m pytest tests -x -q

Write-Host "== mutmut run =="
try {
    mutmut --paths-to-mutate=come/adapters.py `
           --runner="python -m pytest tests -x -q" `
           run
} catch {}

Write-Host "== mutmut results =="
mutmut results
