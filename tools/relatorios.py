"""Ferramentas MCP — Relatórios AFD e Dispositivos."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid
from tools._utils import to_iso_optional

_AFD = "/report/afd"
_AFD_COLETOR = "/report/afd_coletor_marcacao"
_DEVICE = "/device"


def _build_afd_params(
    id_equipamento: int,
    data_ini: str | None,
    data_final: str | None,
    nsr_inicial: int | None,
    limit: int | None,
) -> dict[str, Any]:
    """Monta os query params comuns a todos os relatórios AFD."""
    params: dict[str, Any] = {"idEquipamento": id_equipamento}
    if data_ini:
        params["dataIni"] = to_iso_optional(data_ini)
    if data_final:
        params["dataFinal"] = to_iso_optional(data_final)
    if nsr_inicial is not None:
        params["nsrInicial"] = nsr_inicial
    if limit is not None:
        params["limit"] = limit
    return params


def register_report_tools(mcp: FastMCP) -> None:

    # ── Relatórios AFD ───────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_relatorio_afd_1510(
        id_equipamento: int,
        data_ini: str | None = None,
        data_final: str | None = None,
        nsr_inicial: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """
        Relatório AFD conforme Portaria 1510.

        Args:
            id_equipamento: ID do relógio/dispositivo no RHID.
            data_ini:    Data de início (DD/MM/YYYY). Opcional.
            data_final:  Data de fim (DD/MM/YYYY). Opcional.
            nsr_inicial: NSR de início para extração incremental. Opcional.
            limit:       Limite de registros. Opcional.
        """
        params = _build_afd_params(
            id_equipamento,
            data_ini,
            data_final,
            nsr_inicial,
            limit,
        )
        return await rhid.get(f"{_AFD}/download", params=params)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_relatorio_afd_671(
        id_equipamento: int,
        data_ini: str | None = None,
        data_final: str | None = None,
        nsr_inicial: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """
        Relatório AFD conforme Portaria 671 (substitui a 1510 desde 2023).
        Parâmetros idênticos ao rhid_relatorio_afd_1510.
        """
        params = _build_afd_params(
            id_equipamento,
            data_ini,
            data_final,
            nsr_inicial,
            limit,
        )
        return await rhid.get(f"{_AFD}/download671", params=params)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_relatorio_afd_coletor_1510(
        id_equipamento: int,
        data_ini: str | None = None,
        data_final: str | None = None,
        nsr_inicial: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """AFD Portaria 1510 para REP-P (coletores de marcação móvel)."""
        params = _build_afd_params(
            id_equipamento,
            data_ini,
            data_final,
            nsr_inicial,
            limit,
        )
        return await rhid.get(f"{_AFD_COLETOR}/download", params=params)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_relatorio_afd_coletor_671(
        id_equipamento: int,
        data_ini: str | None = None,
        data_final: str | None = None,
        nsr_inicial: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """AFD Portaria 671 para REP-P (coletores de marcação móvel)."""
        params = _build_afd_params(
            id_equipamento,
            data_ini,
            data_final,
            nsr_inicial,
            limit,
        )
        return await rhid.get(f"{_AFD_COLETOR}/download671", params=params)

    # ── Dispositivos ─────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_dispositivos(
        start: int = 0,
        length: int = 50,
    ) -> Any:
        """
        Lista os relógios de ponto biométrico cadastrados.

        Returns:
            DeviceResult com totalRecords e lista de DeviceDTO
            (id, name, serial, version, status, lastConnectionDate, etc.).
        """
        return await rhid.get(
            _DEVICE,
            params={"start": start, "length": length},
        )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_buscar_dispositivo(device_id: int) -> Any:
        """
        Busca os detalhes de um dispositivo pelo ID.

        Returns:
            DeviceDTO com status de conexão, sincronização e pessoas vinculadas.
        """
        return await rhid.get(f"{_DEVICE}/{device_id}")
