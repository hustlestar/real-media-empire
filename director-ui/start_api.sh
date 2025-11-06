#!/bin/bash
# Start the FastAPI server

cd "$(dirname "$0")"
PYTHONPATH=src .venv/bin/python -m api.main