"""
RHID MCP Server — BHCL / Biowise
Integração com a API RHiD (ControlID).
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from tools.colaboradores import register_person_tools
from tools.escalas import register_escala_tools
from tools.organizacao import register_org_tools
from tools.ponto import register_ponto_tools
from tools.relatorios import register_report_tools

_DOCS = Path(__file__).parent / "docs"

__version__ = "1.0.0"

# ── Logging ──────────────────────────────────────────────────────
# stdio → log para stderr (stdout reservado para o protocolo MCP)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("rhid-mcp")

# ── Servidor MCP ─────────────────────────────────────────────────

mcp = FastMCP(
    name="rhid-bhcl",
    # DNS rebinding protection disabled: service runs behind a reverse proxy
    # with API key authentication handled by _ApiKeyMiddleware in http_server.py
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    instructions="""
Servidor RHID-BHCL: integração com ControlID para ponto eletrônico e RH da BHCL/Biowise.

LOCALIZAR COLABORADOR — a API não tem busca por nome. Pagine rhid_listar_colaboradores
(start=0, length=50, incrementar de 50 em 50). A resposta tem chave "records" (lista).
Nomes estão em MAIÚSCULAS. O campo de ID é "id".

APURAÇÃO DE PONTO — rhid_apuracao_ponto(id_person, data_ini, data_final).
Retorna [] quando o colaborador não usa biometria ou a empresa não tem ponto eletrônico.
Isso não é erro — é resposta válida da API.

DATAS — formato DD/MM/YYYY em todos os parâmetros.

DOCUMENTAÇÃO COMPLETA — consulte o resource rhid://manual (tools, DTOs, fluxos).
""",
)

register_ponto_tools(mcp)
register_person_tools(mcp)
register_org_tools(mcp)
register_report_tools(mcp)
register_escala_tools(mcp)

# ── Resources (documentação inline para o agente) ─────────────────


@mcp.resource(
    "rhid://manual",
    name="Manual do RHID MCP",
    description="Documentação completa: tools, DTOs, fluxos e exemplos de uso.",
    mime_type="text/markdown",
)
def get_manual() -> str:
    """Retorna o manual completo do servidor em Markdown."""
    return (_DOCS / "manual.md").read_text(encoding="utf-8")


# ── Health check (disponível como tool para verificação interna) ─


@mcp.tool()
async def rhid_health_check() -> dict:
    """
    Verifica se o servidor MCP e a conexão com a API RHID estão operacionais.
    Útil para monitoramento e validação pós-deploy.
    """
    from rhid_client import rhid

    try:
        result = await rhid.get("/company", params={"start": "0", "length": "1"})
        total = result.get("totalRecords", 0) if isinstance(result, dict) else -1
        return {
            "status": "healthy",
            "version": __version__,
            "rhid_api": "connected",
            "companies_count": total,
        }
    except Exception as exc:
        return {
            "status": "degraded",
            "version": __version__,
            "rhid_api": "error",
            "detail": str(exc),
        }


# ── Entry point ──────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("RHID MCP Server v%s iniciando", __version__)
    mcp.run(transport="stdio")
