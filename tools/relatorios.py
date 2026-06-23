"""Ferramentas MCP — Relatórios AFD, Dispositivos e Relatórios Essenciais de Ponto.

Inclui:
- Relatórios AFD (Portarias 1510 e 671) e dispositivos
- Proxy genérico + helpers específicos para relatórios de ponto via report.svc/ponto
- Consulta de jobs via notify.svc
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid
from tools._utils import to_iso, to_iso_optional

# ── Paths ──────────────────────────────────────────────────────────────
_AFD = "/report/afd"
_AFD_COLETOR = "/report/afd_coletor_marcacao"
_DEVICE = "/device"

_REPORT_PONTO = "/report/ponto"
_NOTIFY = "/notify"

_TIPOS_RELATORIO = {
    "espelho": "Espelho de Ponto",
    "cartao": "Cartão de Ponto",
    "extrato": "Extrato por Período",
    "diario": "Ponto Diário",
    "inconsistencias": "Relatório de Inconsistências",
    "absenteismo": "Absenteísmo",
}


# ── Helpers internos ────────────────────────────────────────────────────


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


def _build_ponto_payload(
    tipo: str,
    empresa_id: int,
    data_inicio: str,
    data_fim: str,
    formato: str = "pdf",
    destino: str = "download",
    **extra: Any,
) -> dict[str, Any]:
    """Monta o body comum a todos os relatórios de ponto (report.svc/ponto)."""
    payload: dict[str, Any] = {
        "tipo": tipo,
        "idEmpresa": empresa_id,
        "dataInicio": to_iso(data_inicio),
        "dataFim": to_iso(data_fim),
        "formato": formato,
        "destino": destino,
    }
    payload.update(extra)
    return payload


def register_report_tools(mcp: FastMCP) -> None:

    # ═══════════════════════════════════════════════════════════════════
    # Relatórios AFD (Portarias 1510 e 671)
    # ═══════════════════════════════════════════════════════════════════

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

    # ═══════════════════════════════════════════════════════════════════
    # Dispositivos
    # ═══════════════════════════════════════════════════════════════════

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

    # ═══════════════════════════════════════════════════════════════════
    # Relatórios Essenciais de Ponto (Fase 2) — report.svc/ponto
    # ═══════════════════════════════════════════════════════════════════

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            openWorldHint=True,
        ),
    )
    async def rhid_gerar_relatorio_ponto(
        tipo: str,
        empresa_id: int,
        data_inicio: str,
        data_fim: str,
        formato: str = "pdf",
        destino: str = "download",
    ) -> Any:
        """
        Proxy genérico para gerar qualquer relatório de ponto no RHID.

        Envia o POST para report.svc/ponto e retorna o job ID ou status
        para acompanhamento posterior via rhid_consultar_processamento_relatorio.

        Args:
            tipo:       Tipo do relatório.
                        Valores: 'espelho' | 'cartao' | 'extrato' |
                                 'diario' | 'inconsistencias' | 'absenteismo'.
            empresa_id: ID da empresa/unidade no RHID.
            data_inicio: Data de início no formato DD/MM/YYYY.
            data_fim:    Data de fim no formato DD/MM/YYYY.
            formato:     Formato de saída. Padrão: 'pdf'.
            destino:     Destino do relatório. Padrão: 'download'.

        Returns:
            Resposta da API — contém jobId, status, ou mensagem de
            notificação (customerdb/notify.svc/specificGuid/).
        """
        if tipo not in _TIPOS_RELATORIO:
            tipos_validos = ", ".join(_TIPOS_RELATORIO)
            raise ValueError(f"Tipo inválido '{tipo}'. Valores válidos: {tipos_validos}")

        payload = _build_ponto_payload(tipo, empresa_id, data_inicio, data_fim, formato, destino)
        return await rhid.post(_REPORT_PONTO, body=payload)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            openWorldHint=True,
        ),
    )
    async def rhid_gerar_espelho_ponto(
        empresa_id: int,
        data_inicio: str,
        data_fim: str,
        formato: str = "pdf",
        destino: str = "download",
        considerar_justificativas: bool = True,
    ) -> Any:
        """
        Gera o Espelho de Ponto de um colaborador ou empresa.

        POST para report.svc/ponto com tipo='espelho'.
        Exibe as marcações de ponto de forma detalhada, dia a dia.

        Args:
            empresa_id:              ID da empresa/unidade no RHID.
            data_inicio:             Data de início no formato DD/MM/YYYY.
            data_fim:                Data de fim no formato DD/MM/YYYY.
            formato:                 Formato de saída (pdf, xlsx). Padrão: 'pdf'.
            destino:                 Destino (download, email). Padrão: 'download'.
            considerar_justificativas: Incluir justificativas de falta no relatório.

        Returns:
            Resposta da API com jobId e status do processamento.
        """
        payload = _build_ponto_payload(
            "espelho",
            empresa_id,
            data_inicio,
            data_fim,
            formato,
            destino,
            considerarJustificativas=considerar_justificativas,
        )
        return await rhid.post(_REPORT_PONTO, body=payload)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            openWorldHint=True,
        ),
    )
    async def rhid_gerar_cartao_ponto(
        empresa_id: int,
        data_inicio: str,
        data_fim: str,
        formato: str = "pdf",
        destino: str = "download",
        totalizador_centesimal: bool = True,
        colunas: str | None = None,
    ) -> Any:
        """
        Gera o Cartão de Ponto com totalizador centesimal.

        POST para report.svc/ponto com tipo='cartao'.
        Formato tradicional de cartão de ponto, com colunas configuráveis
        e totalização centesimal das horas.

        Args:
            empresa_id:              ID da empresa/unidade no RHID.
            data_inicio:             Data de início no formato DD/MM/YYYY.
            data_fim:                Data de fim no formato DD/MM/YYYY.
            formato:                 Formato de saída (pdf, xlsx). Padrão: 'pdf'.
            destino:                 Destino (download, email). Padrão: 'download'.
            totalizador_centesimal:  Exibir horas no formato centesimal (ex: 8.50).
                                     Padrão: True.
            colunas:                 Lista de colunas a exibir, separadas por vírgula.
                                     Ex: "data,entrada,saida,horas,extras".
                                     Padrão: None (usa colunas padrão).

        Returns:
            Resposta da API com jobId e status do processamento.
        """
        extra: dict[str, Any] = {"totalizadorCentesimal": totalizador_centesimal}
        if colunas:
            extra["colunas"] = colunas
        payload = _build_ponto_payload(
            "cartao",
            empresa_id,
            data_inicio,
            data_fim,
            formato,
            destino,
            **extra,
        )
        return await rhid.post(_REPORT_PONTO, body=payload)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            openWorldHint=True,
        ),
    )
    async def rhid_gerar_extrato_periodo(
        empresa_id: int,
        data_inicio: str,
        data_fim: str,
        formato: str = "pdf",
        destino: str = "download",
        agrupar_por: str = "colaborador",
    ) -> Any:
        """
        Gera o Extrato por Período.

        POST para report.svc/ponto com tipo='extrato'.
        Resumo consolidado de horas trabalhadas, faltas, atrasos e extras
        de todos os colaboradores no período.

        Args:
            empresa_id:   ID da empresa/unidade no RHID.
            data_inicio:  Data de início no formato DD/MM/YYYY.
            data_fim:     Data de fim no formato DD/MM/YYYY.
            formato:      Formato de saída (pdf, xlsx). Padrão: 'pdf'.
            destino:      Destino (download, email). Padrão: 'download'.
            agrupar_por:  Agrupamento dos dados ('colaborador', 'departamento',
                          'centro_custo'). Padrão: 'colaborador'.

        Returns:
            Resposta da API com jobId e status do processamento.
        """
        payload = _build_ponto_payload(
            "extrato",
            empresa_id,
            data_inicio,
            data_fim,
            formato,
            destino,
            agruparPor=agrupar_por,
        )
        return await rhid.post(_REPORT_PONTO, body=payload)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            openWorldHint=True,
        ),
    )
    async def rhid_gerar_relatorio_inconsistencias(
        empresa_id: int,
        data_inicio: str,
        data_fim: str,
        formato: str = "pdf",
        destino: str = "download",
        apenas_nao_resolvidas: bool = True,
    ) -> Any:
        """
        Gera o Relatório de Inconsistências de Marcação.

        POST para report.svc/ponto com tipo='inconsistencias'.
        Lista marcações inconsistentes (divergências, marcações sem
        correspondência, excesso de horário, etc.) no período.

        Args:
            empresa_id:                ID da empresa/unidade no RHID.
            data_inicio:               Data de início no formato DD/MM/YYYY.
            data_fim:                  Data de fim no formato DD/MM/YYYY.
            formato:                   Formato de saída (pdf, xlsx). Padrão: 'pdf'.
            destino:                   Destino (download, email). Padrão: 'download'.
            apenas_nao_resolvidas:     Filtrar apenas inconsistências ainda não
                                       resolvidas. Padrão: True.

        Returns:
            Resposta da API com jobId e status do processamento.
        """
        payload = _build_ponto_payload(
            "inconsistencias",
            empresa_id,
            data_inicio,
            data_fim,
            formato,
            destino,
            apenasNaoResolvidas=apenas_nao_resolvidas,
        )
        return await rhid.post(_REPORT_PONTO, body=payload)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            openWorldHint=True,
        ),
    )
    async def rhid_gerar_relatorio_absenteismo(
        empresa_id: int,
        data_inicio: str,
        data_fim: str,
        formato: str = "pdf",
        destino: str = "download",
        incluir_justificados: bool = True,
    ) -> Any:
        """
        Gera o Relatório de Absenteísmo.

        POST para report.svc/ponto com tipo='absenteismo'.
        Análise de faltas e ausências no período, com indicadores
        de frequência por colaborador, departamento ou centro de custo.

        Args:
            empresa_id:           ID da empresa/unidade no RHID.
            data_inicio:          Data de início no formato DD/MM/YYYY.
            data_fim:             Data de fim no formato DD/MM/YYYY.
            formato:              Formato de saída (pdf, xlsx). Padrão: 'pdf'.
            destino:              Destino (download, email). Padrão: 'download'.
            incluir_justificados: Incluir faltas justificadas no cômputo
                                  do absenteísmo. Padrão: True.

        Returns:
            Resposta da API com jobId e status do processamento.
        """
        payload = _build_ponto_payload(
            "absenteismo",
            empresa_id,
            data_inicio,
            data_fim,
            formato,
            destino,
            incluirJustificados=incluir_justificados,
        )
        return await rhid.post(_REPORT_PONTO, body=payload)

    # ═══════════════════════════════════════════════════════════════════
    # Consulta de Job (notify.svc)
    # ═══════════════════════════════════════════════════════════════════

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=True,
            openWorldHint=True,
        ),
    )
    async def rhid_consultar_processamento_relatorio(guid: str) -> Any:
        """
        Consulta o status de processamento de um relatório gerado.

        GET para notify.svc/{guid}/ — retorna o status do job assíncrono
        de geração do relatório.

        Use este endpoint após rhid_gerar_relatorio_ponto() ou qualquer
        helper específico para verificar se o relatório já foi processado
        e está pronto para download.

        Args:
            guid: GUID retornado pelo endpoint de geração do relatório
                  (campo jobId ou notificationGuid na resposta do POST).

        Returns:
            Status do processamento: {status, fileName, downloadUrl, ...}
            Status possíveis: "processing", "completed", "error".
        """
        return await rhid.get(f"{_NOTIFY}/{guid}/")
