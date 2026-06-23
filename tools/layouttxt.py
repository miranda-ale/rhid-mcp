"""Ferramentas MCP — Layouts TXT (LayoutTXT)."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid

_PATH = "/customerdb/layouttxt.svc"


def register_layouttxt_tools(mcp: FastMCP) -> None:
    """Registra todas as tools de Layouts TXT no servidor MCP."""

    # ── List ──────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_layouts_txt(
        start: int = 0,
        length: int = 50,
    ) -> Any:
        """
        Lista todos os layouts de arquivo TXT cadastrados com paginação.

        Args:
            start:  Índice de início (offset). Padrão: 0.
            length: Quantidade de registros. Padrão: 50.

        Returns:
            Objeto paginado com totalRecords e lista de LayoutTxtDTO:
            - id (int): ID do layout
            - description (str): Nome/descrição
            - idCompany (int): ID da empresa vinculada
            - layout (str): Definição do layout
        """
        return await rhid.get(f"{_PATH}/a", params={
            "start": start,
            "length": length,
        })

    # ── Create ────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def rhid_criar_layouts_txt(
        registros: list[dict[str, Any]],
    ) -> Any:
        """
        Cria um ou mais layouts de arquivo TXT.

        Args:
            registros: Lista de dicionários com campos:
                - description (str): Nome/descrição (obrigatório)
                - idCompany (int): ID da empresa (opcional)
                - layout (str): Definição do layout (obrigatório)
        """
        return await rhid.post(f"{_PATH}/c", body=registros)

    # ── Update ────────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            idempotentHint=True,
        ),
    )
    async def rhid_atualizar_layout_txt(
        registro: dict[str, Any],
    ) -> Any:
        """
        Atualiza um layout TXT existente (PUT).

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
    async def rhid_remover_layout_txt(
        layout_id: int,
    ) -> Any:
        """
        Remove um layout TXT. Operação destrutiva.

        Args:
            layout_id: ID do layout a remover.
        """
        return await rhid.delete(f"{_PATH}/d?id={layout_id}")
