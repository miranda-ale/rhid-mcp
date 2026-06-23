"""Ferramentas MCP — Escalas de Horário (Shift)."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid

_PATH = "/customerdb/shift.svc"


def register_escala_tools(mcp: FastMCP) -> None:
    """Registra todas as tools de Escalas no servidor MCP."""

    # ── List ──────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_escalas(
        start: int = 0,
        length: int = 50,
    ) -> Any:
        """
        Lista todas as escalas de horário cadastradas com paginação.

        Args:
            start:  Índice de início (offset). Padrão: 0.
            length: Quantidade de registros. Padrão: 50.

        Returns:
            Resultado paginado com totalRecords e lista de escalas
            (id, codigo, description, idCompany, companyName, etc.).
        """
        return await rhid.get(
            f"{_PATH}/a_escalas",
            params={
                "start": start,
                "length": length,
            },
        )

    # ── Buscar por código ─────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_buscar_escala(codigo: str) -> Any:
        """
        Busca uma escala específica pelo código.

        Args:
            codigo: Código da escala (ex: 'TT-001').

        Returns:
            A escala encontrada ou objeto com campo 'erro'.
        """
        escalas = await rhid.get(f"{_PATH}/a_escalas")
        for e in escalas.get("data", escalas):
            if e.get("codigo") == codigo or e.get("id") == codigo:
                return e
        return {"erro": f"Escala '{codigo}' não encontrada"}

    # ── Create ────────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def rhid_criar_escalas(
        registros: list[dict[str, Any]],
    ) -> Any:
        """
        Cria uma ou mais escalas de horário.

        Args:
            registros: Lista de dicionários com campos da escala.
                Campos comuns: codigo (str), description (str),
                idCompany (int), idDepartment (int, opcional).
        """
        return await rhid.post(f"{_PATH}/c", body=registros)

    # ── Update ────────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            idempotentHint=True,
        ),
    )
    async def rhid_atualizar_escala(
        registro: dict[str, Any],
    ) -> Any:
        """
        Atualiza uma escala de horário existente (PUT).

        Args:
            registro: Dicionário com campos da escala. Campo 'id' obrigatório.
        """
        return await rhid.put(f"{_PATH}/u", body=registro)

    # ── Delete ────────────────────────────────────────────────────────

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
        ),
    )
    async def rhid_remover_escala(
        escala_id: int,
    ) -> Any:
        """
        Remove uma escala de horário. Operação destrutiva.

        Args:
            escala_id: ID da escala a remover.
        """
        return await rhid.delete(f"{_PATH}/d?id={escala_id}")
