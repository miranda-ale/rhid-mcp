"""Ferramentas MCP — Apuração de Ponto."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid


def register_ponto_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    async def rhid_apuracao_ponto(
        id_person: int,
        data_ini: str,
        data_final: str,
    ) -> Any:
        """
        Retorna a apuração de ponto (registros de entrada/saída) de um colaborador
        em um intervalo de datas.

        Args:
            id_person: ID numérico do colaborador no RHID.
            data_ini:  Data de início no formato DD/MM/YYYY.
            data_final: Data de fim no formato DD/MM/YYYY.

        Returns:
            Registros de ponto com horários, horas trabalhadas e ocorrências.
        """
        return await rhid.get(
            "/apuracao_ponto",
            params={
                "idPerson": id_person,
                "dataIni": data_ini,
                "dataFinal": data_final,
            },
        )