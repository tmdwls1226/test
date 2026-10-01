#!/usr/bin/env bash
# 프론트(vite)와 백엔드(FastAPI)를 함께 실행한다. DB가 비어 있으면 샘플 데이터를 먼저 적재한다.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d backend/.venv ]; then
  python3 -m venv backend/.venv
  backend/.venv/bin/pip install -q -r backend/requirements.txt
fi
[ -d node_modules ] || npm install

(cd backend && .venv/bin/python -m app.ingest --sample --if-empty)

trap 'kill 0' EXIT
(cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000) &
npx vite
