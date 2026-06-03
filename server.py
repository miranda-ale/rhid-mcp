"""
RHID MCP Server — BHCL / Biowise
Integração com a API RHiD (ControlID).
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from tools.colaboradores import register_person_tools
from tools.organizacao import register_org_tools
from tools.ponto import register_ponto_tools
from tools.relatorios import register_report_tools

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


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8765"))

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="streamable-http", host=host, port=port)