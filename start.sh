#!/bin/bash
set -e
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd frontend && npm run dev
wait $BACKEND_PID
