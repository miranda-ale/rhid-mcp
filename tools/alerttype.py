"""Ferramentas MCP — Tipos de Inconsistência (AlertType)."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid

_PATH = "/customerdb/alerttype.svc"


def register_alerttype_tools(mcp: FastMCP) -> None:
    """Registra todas as tools de Tipos de Inconsistência no servidor MCP."""

    # ── List ──────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_tipos_inconsistencia(
        start: int = 0,
        length: int = 50,
    ) -> Any:
        """
        Lista todos os tipos de inconsistência/alerta cadastrados com paginação.

        Args:
            start:  Índice de início (offset). Padrão: 0.
            length: Quantidade de registros. Padrão: 50.

        Returns:
            Objeto paginado com totalRecords e lista de AlertTypeDTO:
            - id (int): ID do tipo de inconsistência
            - description (str): Nome/descrição
            - idCompany (int): ID da empresa vinculada
        """
        return await rhid.get(f"{_PATH}/a", params={
            "start": start,
            "length": length,
        })

    # ── Create ────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def rhid_criar_tipos_inconsistencia(
        registros: list[dict[str, Any]],
    ) -> Any:
        """
        Cria um ou mais tipos de inconsistência/alerta.

        Args:
            registros: Lista de dicionários com campos:
                - description (str): Nome/descrição (obrigatório)
                - idCompany (int): ID da empresa (opcional)
        """
        return await rhid.post(f"{_PATH}/c", body=registros)

    # ── Update ────────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            idempotentHint=True,
        ),
    )
    async def rhid_atualizar_tipo_inconsistencia(
        registro: dict[str, Any],
    ) -> Any:
        """
        Atualiza um tipo de inconsistência existente (PUT).

        Args:
            registro: Dicionário com campos. Campo 'id' obrigatório.
        """
        return await rhid.put(f"{_PATH}/u", body=registro)

    # ── Delete ────────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
        ),
    )
    async def rhid_remover_tipo_inconsistencia(
        alert_id: int,
    ) -> Any:
        """
        Remove um tipo de inconsistência. Operação destrutiva.

        Args:
            alert_id: ID do tipo de inconsistência a remover.
        """
        return await rhid.delete(f"{_PATH}/d?id={alert_id}")
