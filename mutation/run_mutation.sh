#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

pip install -q -r requirements.txt

echo "== sanity: pytest =="
python -m pytest tests -x -q

echo "== mutmut run =="
mutmut --paths-to-mutate=come/adapters.py \
       --runner="python -m pytest tests -x -q" \
       run || true

echo "== mutmut results =="
mutmut results
