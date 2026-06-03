# ============================================================
# RHID MCP Server — Makefile
# ============================================================

.PHONY: help install dev test lint build up down logs health clean

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ── Local ────────────────────────────────────────────────────

install: ## Cria venv e instala dependências
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

dev: ## Roda servidor local (stdio)
	MCP_TRANSPORT=stdio .venv/bin/python server.py

test: ## Testa conexão com a API RHID
	.venv/bin/python test_client.py

lint: ## Roda linter (ruff)
	.venv/bin/pip install ruff -q
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .

inspect: ## Abre MCP Inspector no browser
	npx @modelcontextprotocol/inspector python server.py

# ── Docker ───────────────────────────────────────────────────

build: ## Build da imagem Docker
	docker build -t rhid-mcp:latest .

up: ## Sobe o container (docker compose)
	docker compose up -d

down: ## Para o container
	docker compose down

logs: ## Mostra logs do container
	docker compose logs -f --tail=50

health: ## Verifica health check do container
	@docker inspect --format='{{.State.Health.Status}}' rhid-mcp 2>/dev/null || echo "Container não encontrado"

# ── Manutenção ───────────────────────────────────────────────

clean: ## Remove caches e artefatos
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .venv .ruff_cache .pyright