FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /fasm

# Install the application dependencies.
WORKDIR /fasm
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "--port", "80", "--host", "0.0.0.0", "--workers", "4"]