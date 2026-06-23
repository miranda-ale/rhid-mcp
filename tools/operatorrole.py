"""Ferramentas MCP — Permissões de Operador (OperatorRole)."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid

_PATH = "/customerdb/operatorrole.svc"


def register_operatorrole_tools(mcp: FastMCP) -> None:
    """Registra todas as tools de Permissões de Operador no servidor MCP."""

    # ── List (read-only: endpoint confirmado) ─────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_permissoes_operador() -> Any:
        """
        Lista as permissões avançadas disponíveis para operadores do sistema.

        Retorna as permissões disponíveis que podem ser atribuídas
        a operadores/perfis de acesso no RHID.

        Note:
            Este endpoint é read-only conforme confirmado nos DevTools.
        """
        return await rhid.get(f"{_PATH}/getAdvancedPermissions")
