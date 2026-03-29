#!/usr/bin/env bash
# Start both Vite dev server and Python backend
cd "$(dirname "$0")/.."

echo "Starting Python backend on :8000..."
python dashboard/server.py &
PYTHON_PID=$!

echo "Starting Vite dev server on :5173..."
npx vite --host &
VITE_PID=$!

trap "kill $PYTHON_PID $VITE_PID 2>/dev/null" EXIT
wait
