"""
RHID MCP Server — BHCL / Biowise
Integração com a API RHiD (ControlID).
"""

from __future__ import annotations

import logging
import os
import sys

from mcp.server.fastmcp import FastMCP

from tools.colaboradores import register_person_tools
from tools.organizacao import register_org_tools
from tools.ponto import register_ponto_tools
from tools.relatorios import register_report_tools

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
    instructions=(
        "Servidor de integração com o sistema RHID (ControlID) da BHCL/Biowise. "
        "Fornece acesso a apuração de ponto, colaboradores, estrutura organizacional "
        "(departamentos, centros de custo, cargos, empresas), relatórios AFD e "
        "dispositivos de ponto. Datas no formato DD/MM/YYYY salvo indicação contrária."
    ),
)

register_ponto_tools(mcp)
register_person_tools(mcp)
register_org_tools(mcp)
register_report_tools(mcp)

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
