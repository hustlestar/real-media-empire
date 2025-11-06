#!/bin/bash

# Start backend API server in background
echo "Starting backend API server..."
PYTHONPATH=src .venv/bin/python -m api.main &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend dev server
echo "Starting frontend dev server..."
cd frontend && npm run dev

# When frontend is stopped (Ctrl+C), also stop backend
kill $BACKEND_PID
