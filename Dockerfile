FROM python:3.10-slim-bookworm

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /app
RUN mkdir -p /app/data
RUN uv sync --locked --no-dev
EXPOSE 8001
CMD ["uv", "run", "streamlit","run", "frontend.py", "--server.port", "8001"]
