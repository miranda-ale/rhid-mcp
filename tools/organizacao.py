"""Ferramentas MCP — Departamentos, Centros de Custo, Cargos e Empresas."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from rhid_client import rhid

_DEPARTMENT = "/department"
_COSTCENTERS = "/costcenters"
_PERSONROLES = "/personroles"
_COMPANY = "/company"


def register_org_tools(mcp: FastMCP) -> None:

    # ── Departamentos ────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_departamentos(
        start: int = 0,
        length: int = 100,
    ) -> Any:
        """
        Lista todos os departamentos cadastrados.

        Returns:
            DepartmentResult com totalRecords e lista de DepartmentDTO
            (id, name, idCompany, folha, companyName, idApprovalFlow).
        """
        return await rhid.get(
            _DEPARTMENT,
            params={"start": start, "length": length},
        )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_buscar_departamento(dept_id: int) -> Any:
        """Busca um departamento específico pelo ID."""
        return await rhid.get(f"{_DEPARTMENT}/{dept_id}")

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def rhid_criar_departamentos(
        departamentos: list[dict[str, Any]],
    ) -> Any:
        """
        Cria um ou mais departamentos.

        Args:
            departamentos: Lista de DepartmentDTO.
                Campos: name (str), idCompany (int), folha (str, opcional).
        """
        return await rhid.post(_DEPARTMENT, body=departamentos)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True))
    async def rhid_atualizar_departamento(departamento: dict[str, Any]) -> Any:
        """Atualiza um departamento existente. Campo 'id' obrigatório."""
        return await rhid.put(_DEPARTMENT, body=departamento)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
    async def rhid_remover_departamento(dept_id: int) -> Any:
        """Remove um departamento pelo ID."""
        return await rhid.delete(f"{_DEPARTMENT}/{dept_id}")

    # ── Centros de Custo ─────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_centros_custo(
        start: int = 0,
        length: int = 50,
    ) -> Any:
        """
        Lista todos os centros de custo cadastrados com paginação.

        Args:
            start:  Índice de início (offset). Padrão: 0.
            length: Quantidade de registros. Padrão: 50.

        Returns:
            Resultado paginado com totalRecords e lista de CostCenterDTO
            (id, companyName, idCompany, name).
        """
        return await rhid.get(
            _COSTCENTERS,
            params={"start": start, "length": length},
        )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_buscar_centro_custo(cc_id: int) -> Any:
        """
        Busca um centro de custo pelo ID.

        Returns:
            CostCenterDTO (id, companyName, idCompany, name).
        """
        return await rhid.get(f"{_COSTCENTERS}/{cc_id}")

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def rhid_criar_centros_custo(
        centros: list[dict[str, Any]],
    ) -> Any:
        """
        Cria centros de custo.

        Args:
            centros: Lista de CostCenterDTO. Campos: name (str), idCompany (int).
        """
        return await rhid.post(_COSTCENTERS, body=centros)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True))
    async def rhid_atualizar_centro_custo(centro: dict[str, Any]) -> Any:
        """Atualiza um centro de custo. Campo 'id' obrigatório."""
        return await rhid.put(_COSTCENTERS, body=centro)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
    async def rhid_remover_centro_custo(cc_id: int) -> Any:
        """Remove um centro de custo pelo ID."""
        return await rhid.delete(f"{_COSTCENTERS}/{cc_id}")

    # ── Cargos (Person Roles) ────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_cargos(
        start: int = 0,
        length: int = 50,
    ) -> Any:
        """
        Lista todos os cargos cadastrados com paginação.

        Args:
            start:  Índice de início (offset). Padrão: 0.
            length: Quantidade de registros. Padrão: 50.

        Returns:
            Resultado paginado com totalRecords e lista de PersonRoleDTO
            (id, companyName, idCompany, name).
        """
        return await rhid.get(
            _PERSONROLES,
            params={"start": start, "length": length},
        )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_buscar_cargo(role_id: int) -> Any:
        """
        Busca um cargo pelo ID.

        Returns:
            PersonRoleDTO (id, companyName, idCompany, name).
        """
        return await rhid.get(f"{_PERSONROLES}/{role_id}")

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def rhid_criar_cargos(cargos: list[dict[str, Any]]) -> Any:
        """
        Cria cargos.

        Args:
            cargos: Lista de PersonRoleDTO. Campos: name (str), idCompany (int).
        """
        return await rhid.post(_PERSONROLES, body=cargos)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True))
    async def rhid_atualizar_cargo(cargo: dict[str, Any]) -> Any:
        """Atualiza um cargo. Campo 'id' obrigatório."""
        return await rhid.put(_PERSONROLES, body=cargo)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
    async def rhid_remover_cargo(role_id: int) -> Any:
        """Remove um cargo pelo ID."""
        return await rhid.delete(f"{_PERSONROLES}/{role_id}")

    # ── Empresas ─────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_empresas(start: int = 0, length: int = 50) -> Any:
        """
        Lista as empresas (unidades) cadastradas no RHID.

        Returns:
            CompanyResult com totalRecords e lista de CompanyDTO
            (id, cnpj, name, tradingName, city, state, etc.).
        """
        return await rhid.get(
            _COMPANY,
            params={"start": start, "length": length},
        )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_buscar_empresa(company_id: int) -> Any:
        """Busca uma empresa pelo ID."""
        return await rhid.get(f"{_COMPANY}/{company_id}")

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False))
    async def rhid_criar_empresas(empresas: list[dict[str, Any]]) -> Any:
        """
        Cria uma ou mais empresas (unidades).

        Args:
            empresas: Lista de CompanyDTO.
                Campos principais: cnpj (int), name (str),
                tradingName (str, opcional), city (str), state (str).
        """
        return await rhid.post(_COMPANY, body=empresas)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            idempotentHint=True,
        ),
    )
    async def rhid_atualizar_empresa(empresa: dict[str, Any]) -> Any:
        """
        Atualiza uma empresa/unidade existente.

        Args:
            empresa: CompanyDTO com campo 'id' obrigatório.
        """
        return await rhid.put(_COMPANY, body=empresa)

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
        ),
    )
    async def rhid_remover_empresa(company_id: int) -> Any:
        """
        Remove uma empresa/unidade. Operação destrutiva.

        Args:
            company_id: ID da empresa a remover.
        """
        return await rhid.delete(f"{_COMPANY}/{company_id}")
