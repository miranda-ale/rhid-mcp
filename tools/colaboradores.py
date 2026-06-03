"""Ferramentas MCP — Colaboradores (Person)."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid

_PATH = "/person"


def register_person_tools(mcp: FastMCP) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_colaboradores(
        start: int = 0,
        length: int = 50,
    ) -> Any:
        """
        Lista todos os colaboradores cadastrados no RHID com paginação.

        Args:
            start:  Índice de início (offset). Padrão: 0.
            length: Quantidade de registros a retornar. Padrão: 50.

        Returns:
            Objeto com totalRecords e lista de PersonDTO.
        """
        return await rhid.get(_PATH, params={"start": start, "length": length})

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_colaboradores_com_templates(
        start: int = 0,
        length: int = 50,
    ) -> Any:
        """
        Lista colaboradores incluindo dados de templates biométricos.

        Args:
            start:  Índice de início (offset). Padrão: 0.
            length: Quantidade de registros a retornar. Padrão: 50.
        """
        return await rhid.get(
            f"{_PATH}/withtemplates",
            params={"start": start, "length": length},
        )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_buscar_colaborador(person_id: int) -> Any:
        """
        Busca os dados completos de um colaborador pelo ID.

        Args:
            person_id: ID numérico do colaborador no RHID.
        """
        return await rhid.get(f"{_PATH}/{person_id}")

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False))
    async def rhid_criar_colaboradores(colaboradores: list[dict[str, Any]]) -> Any:
        """
        Cria um ou mais colaboradores no RHID.

        Args:
            colaboradores: Lista de objetos PersonDTO. Campos principais:
                - cpf (int): CPF sem formatação
                - name (str): Nome completo
                - registration (str): Matrícula
                - idDepartment (int): ID do departamento
                - idCompany (int): ID da empresa
                - pis (int, opcional): PIS/NIS
                - status (int): 1=ativo, 0=inativo
        """
        return await rhid.post(_PATH, body=colaboradores)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True))
    async def rhid_atualizar_colaborador(colaborador: dict[str, Any]) -> Any:
        """
        Atualiza todos os dados de um colaborador existente (PUT).

        Args:
            colaborador: PersonDTO com campo 'id' obrigatório.
        """
        return await rhid.put(_PATH, body=colaborador)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True))
    async def rhid_atualizar_colaboradores_parcial(
        atualizacoes: list[dict[str, Any]],
    ) -> Any:
        """
        Atualiza campos específicos de um ou mais colaboradores (PATCH).

        Args:
            atualizacoes: Lista de objetos com 'id' + campos a atualizar.
                          Exemplo: [{"id": 42, "status": 0}]
        """
        return await rhid.patch(_PATH, body=atualizacoes)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
    async def rhid_remover_colaborador(person_id: int) -> Any:
        """
        Remove um colaborador do RHID pelo ID. Operação destrutiva.

        Args:
            person_id: ID numérico do colaborador.
        """
        return await rhid.delete(f"{_PATH}/{person_id}")
