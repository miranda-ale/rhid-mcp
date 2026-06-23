"""Ferramentas MCP — Feriados (Holiday)."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid

_PATH = "/customerdb/holiday.svc"


def register_holiday_tools(mcp: FastMCP) -> None:
    """Registra todas as tools de Feriados no servidor MCP."""

    # ── List ──────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_feriados(
        start: int = 0,
        length: int = 50,
    ) -> Any:
        """
        Lista todos os feriados cadastrados no RHID com paginação.

        Args:
            start:  Índice de início (offset). Padrão: 0.
            length: Quantidade de registros a retornar. Padrão: 50.

        Returns:
            Objeto paginado (DataTables) com totalRecords e lista de HolidayDTO:
            - id (int): ID do feriado
            - description (str): Nome/descrição do feriado
            - date (str): Data no formato YYYY-MM-DD
            - idCompany (int): ID da empresa vinculada (ou null para todos)
            - type (int): Tipo (0=fixo, 1=móvel, etc.)
            - abrangence (int): Abrangência (1=nacional, 2=estadual, 3=municipal)
        """
        return await rhid.get(f"{_PATH}/a", params={
            "start": start,
            "length": length,
        })

    # ── Create ────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def rhid_criar_feriados(
        registros: list[dict[str, Any]],
    ) -> Any:
        """
        Cria um ou mais feriados no RHID.

        Args:
            registros: Lista de HolidayDTO. Campos principais:
                - description (str): Nome do feriado (obrigatório)
                - date (str): Data no formato YYYY-MM-DD (obrigatório)
                - idCompany (int, opcional): ID da empresa. Null = todas.
                - type (int, opcional): 0=fixo, 1=móvel. Padrão: 0.
                - abrangence (int, opcional): 1=nacional, 2=estadual, 3=municipal.
        """
        return await rhid.post(f"{_PATH}/c", body=registros)

    # ── Update ────────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            idempotentHint=True,
        ),
    )
    async def rhid_atualizar_feriado(
        registro: dict[str, Any],
    ) -> Any:
        """
        Atualiza um feriado existente (PUT).

        Args:
            registro: HolidayDTO completo. Campo 'id' obrigatório.
                     Enviar todos os campos, não apenas os alterados.
        """
        return await rhid.put(f"{_PATH}/u", body=registro)

    # ── Delete ────────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
        ),
    )
    async def rhid_remover_feriado(
        holiday_id: int,
    ) -> Any:
        """
        Remove um feriado do RHID. Operação destrutiva.

        Args:
            holiday_id: ID numérico do feriado a remover.
        """
        return await rhid.delete(f"{_PATH}/d?id={holiday_id}")
