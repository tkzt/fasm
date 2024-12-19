#!/bin/bash
uv run alembic upgrade head
exec /fasm/.venv/bin/fastapi run --port 80 --host 0.0.0.0 --workers 4
