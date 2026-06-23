"""Ferramentas MCP — Motivos de Demissão (ReasonDismissal)."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid

_PATH = "/customerdb/reasondismissal.svc"


def register_reasondismissal_tools(mcp: FastMCP) -> None:
    """Registra todas as tools de Motivos de Demissão no servidor MCP."""

    # ── List ──────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_motivos_demissao(
        start: int = 0,
        length: int = 50,
    ) -> Any:
        """
        Lista todos os motivos de demissão cadastrados com paginação.

        Args:
            start:  Índice de início (offset). Padrão: 0.
            length: Quantidade de registros. Padrão: 50.

        Returns:
            Objeto paginado com totalRecords e lista de ReasonDismissalDTO:
            - id (int): ID do motivo
            - description (str): Nome/descrição
            - idCompany (int): ID da empresa vinculada
        """
        return await rhid.get(
            f"{_PATH}/a",
            params={
                "start": start,
                "length": length,
            },
        )

    # ── Create ────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def rhid_criar_motivos_demissao(
        registros: list[dict[str, Any]],
    ) -> Any:
        """
        Cria um ou mais motivos de demissão.

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
    async def rhid_atualizar_motivo_demissao(
        registro: dict[str, Any],
    ) -> Any:
        """
        Atualiza um motivo de demissão existente (PUT).

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
    async def rhid_remover_motivo_demissao(
        reason_id: int,
    ) -> Any:
        """
        Remove um motivo de demissão. Operação destrutiva.

        Args:
            reason_id: ID do motivo de demissão a remover.
        """
        return await rhid.delete(f"{_PATH}/d?id={reason_id}")
