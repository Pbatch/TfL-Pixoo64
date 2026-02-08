FROM ghcr.io/astral-sh/uv:python3.14-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

FROM python:3.14-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY . .
CMD ["python", "index.py"]