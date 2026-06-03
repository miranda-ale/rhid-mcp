"""Ferramentas MCP — Apuração de Ponto."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid
from tools._utils import to_iso


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
            Lista de registros diários com marcações, horas trabalhadas, faltas e
            justificativas. Cada item tem: date, diasTrabalhados, faltaDiaInteiro,
            listAfdtManutencao (marcações E/S), isHoliday, totalHorasTrabalhadas.
            Registros com _typeEntradaSaida="D" e _typeClassification="J" são
            faltas justificadas; abreviationJustification indica o motivo.
        """
        return await rhid.get(
            "/apuracao_ponto",
            params={
                "idPerson": id_person,
                "dataIni": to_iso(data_ini),
                "dataFinal": to_iso(data_final),
            },
        )
