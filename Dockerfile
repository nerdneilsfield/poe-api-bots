# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

ADD . /app/

RUN uv sync --frozen --no-dev \
    && uv pip install -e .

CMD ["uv", "run", "bot/bot.py", "-c", "/app/configs/config.toml"]