FROM python:3.12-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  libpq-dev \
  gcc \
  python3-dev \
  && rm -rf /var/lib/apt/lists/*

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /fasm

# Install the application dependencies.
WORKDIR /fasm
RUN uv sync --frozen --no-cache --group pg

# Run the application.
RUN chmod +x /fasm/start.sh
CMD ["/fasm/start.sh"]