# ============================================================
# RHID MCP Server — BHCL / Biowise
# Build de produção seguindo boas práticas Docker/OCI
# ============================================================

# ── Stage 1: dependências (cache otimizado) ──────────────────
FROM python:3.13-slim AS deps

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# ── Stage 2: imagem final ────────────────────────────────────
FROM python:3.13-slim

# Metadata OCI (padrão de mercado para labels)
LABEL org.opencontainers.image.title="RHID MCP Server"
LABEL org.opencontainers.image.description="MCP server para integração com a API RHiD (ControlID) — BHCL/Biowise"
LABEL org.opencontainers.image.vendor="BHCL"
LABEL org.opencontainers.image.source="https://github.com/bhcl/rhid-mcp"
LABEL org.opencontainers.image.version="1.0.0"

# Segurança: usuário não-root
RUN groupadd --gid 1000 mcp \
    && useradd --uid 1000 --gid mcp --shell /bin/sh --create-home mcp

WORKDIR /app

# Copiar dependências do stage anterior (cache preservado)
COPY --from=deps /app/deps /app/deps
ENV PYTHONPATH=/app/deps

# Copiar código da aplicação
COPY --chown=mcp:mcp . .

# Sem buffer no Python (logs em tempo real no Docker)
ENV PYTHONUNBUFFERED=1
# Não gerar .pyc (desnecessário em container)
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8765

# Health check: verifica /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:8765/health', timeout=5); assert r.status_code == 200" || exit 1

USER mcp

ENTRYPOINT ["python", "http_server.py"]