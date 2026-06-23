# RHID MCP Server — BHCL/Biowise

> **Nota sobre o nome**: O sistema é **RHID** (RHiD / ControlID), e não RHDI.
> A documentação e o código usam exclusivamente `RHID` e `rhid_*` como prefixo das ferramentas.

Servidor MCP para integração com a API **RHID** (ControlID), expondo **32 ferramentas**
que cobrem apuração de ponto, gestão de colaboradores, estrutura organizacional,
dispositivos, escalas e relatórios AFD — para uso no Claude Desktop, Claude Code
e Claude.ai via Projects.

---

## Cobertura do MCP vs. Sistema Real

### ✅ Coberto — 32 ferramentas

| Categoria | Tools | Operações |
|-----------|-------|-----------|
| **Colaboradores** | 7 | Listar, Listar c/ biometria, Buscar por ID, Criar em lote, Atualizar, Atualização parcial, Remover |
| **Departamentos** | 5 | Listar, Buscar por ID, Criar, Atualizar, Remover |
| **Centros de Custo** | 4 | Buscar por ID, Criar, Atualizar, Remover |
| **Cargos** | 4 | Buscar por ID, Criar, Atualizar, Remover |
| **Empresas (Unidades)** | 2 | Listar, Buscar por ID |
| **Apuração de Ponto** | 1 | Consulta de jornada por colaborador e período |
| **Relatórios AFD** | 4 | AFD 1510, AFD 671, AFD Coletor 1510, AFD Coletor 671 |
| **Dispositivos** | 2 | Listar relógios, Buscar por ID |
| **Escalas de Horário** | 2 | Listar escalas, Buscar por código |
| **Health Check** | 1 | Verificação de conectividade com a API |
| **Total** | **32** | |

### Ferramentas detalhadas

| Tool | Operação | Endpoint |
|------|----------|----------|
| **Colaboradores** | | |
| `rhid_listar_colaboradores` | Lista paginada de colaboradores | `GET /person` |
| `rhid_listar_colaboradores_com_templates` | Lista com biometria | `GET /person/withtemplates` |
| `rhid_buscar_colaborador` | Colaborador por ID | `GET /person/{id}` |
| `rhid_criar_colaboradores` | Cadastro em lote | `POST /person` |
| `rhid_atualizar_colaborador` | Atualização completa | `PUT /person` |
| `rhid_atualizar_colaboradores_parcial` | Atualização parcial | `PATCH /person` |
| `rhid_remover_colaborador` | Remoção | `DELETE /person/{id}` |
| **Departamentos** | | |
| `rhid_listar_departamentos` | Lista departamentos | `GET /department` |
| `rhid_buscar_departamento` | Depto por ID | `GET /department/{id}` |
| `rhid_criar_departamentos` | Cria departamentos | `POST /department` |
| `rhid_atualizar_departamento` | Atualiza depto | `PUT /department` |
| `rhid_remover_departamento` | Remove depto | `DELETE /department/{id}` |
| **Centros de Custo** | | |
| `rhid_buscar_centro_custo` | Centro de custo por ID | `GET /costcenters/{id}` |
| `rhid_criar_centros_custo` | Cria centros de custo | `POST /costcenters` |
| `rhid_atualizar_centro_custo` | Atualiza centro de custo | `PUT /costcenters` |
| `rhid_remover_centro_custo` | Remove centro de custo | `DELETE /costcenters/{id}` |
| **Cargos** | | |
| `rhid_buscar_cargo` | Cargo por ID | `GET /personroles/{id}` |
| `rhid_criar_cargos` | Cria cargos | `POST /personroles` |
| `rhid_atualizar_cargo` | Atualiza cargo | `PUT /personroles` |
| `rhid_remover_cargo` | Remove cargo | `DELETE /personroles/{id}` |
| **Empresas** | | |
| `rhid_listar_empresas` | Lista empresas/unidades | `GET /company` |
| `rhid_buscar_empresa` | Empresa por ID | `GET /company/{id}` |
| **Apuração de Ponto** | | |
| `rhid_apuracao_ponto` | Apuração de jornada por colaborador e período | `GET /apuracao_ponto` |
| **Relatórios AFD** | | |
| `rhid_relatorio_afd_1510` | AFD Portaria 1510 | `GET /report/afd/download` |
| `rhid_relatorio_afd_671` | AFD Portaria 671 | `GET /report/afd/download671` |
| `rhid_relatorio_afd_coletor_1510` | AFD REP-P 1510 | `GET /report/afd_coletor_marcacao/download` |
| `rhid_relatorio_afd_coletor_671` | AFD REP-P 671 | `GET /report/afd_coletor_marcacao/download671` |
| **Dispositivos** | | |
| `rhid_listar_dispositivos` | Lista relógios de ponto | `GET /device` |
| `rhid_buscar_dispositivo` | Dispositivo por ID | `GET /device/{id}` |
| **Escalas** | | |
| `listar_escalas` | Lista todas as escalas de horário | `GET /customerdb/shift.svc/a_escalas` |
| `buscar_escala` | Busca escala por código | `GET /customerdb/shift.svc/a_escalas` (filtro local) |
| **Monitoramento** | | |
| `rhid_health_check` | Verifica conectividade com a API RHID | `GET /company` (interna) |

### ❌ Gaps conhecidos — não cobertos pelo MCP

O sistema RHID (ControlID v26) da BHCL possui funcionalidades **não expostas**
como ferramentas MCP. Abaixo os módulos com maior gap:

#### Cadastros (16 submenus — apenas 4 cobertos)

O módulo **Cadastros** possui 16 submenus. O MCP cobre apenas **4** (Colaboradores,
Departamentos, Cargos, Centros de Custo). Faltam:

| # | Submenu | Observação |
|---|---------|------------|
| 1 | **Faces** | Envio de solicitação de cadastro facial por e-mail |
| 2 | **Motivos de Demissão** | 7 registros (Justa Causa, Pedido Demissão, etc.) |
| 3 | **Feriados** | 22 registros |
| 4 | **Layouts TXT** | Exportação para Folha de Pagamento (Domínio) |
| 5 | **Tipos de Inconsistência** | 4 registros (Atraso, Falta, etc.) |
| 6 | **Tipos de Justificativa** | 107 registros |
| 7 | **Atribuições em Massa** | Wizard 3 passos (Horário, Jornada, Batidas) |
| 8 | **Locais de Trabalho** | CRUD |
| 9 | **Fluxos de Aprovação** | CRUD |
| 10 | **Motivos de Inclusão** | CRUD |
| 11 | **Notificações** | CRUD |

#### Relatórios (25 tipos — nenhum coberto)

O módulo **Relatórios** possui **25 tipos de relatório** parametrizáveis. O MCP
cobre apenas os 4 relatórios AFD (extração de arquivo fiscal). Os **21 tipos
restantes** de relatórios gerenciais e operacionais **não estão disponíveis**:

| # | Relatório | Tipo |
|---|-----------|------|
| 1 | Espelho de Ponto | Parâmetros (PDF/Excel) |
| 2 | Cartão de Ponto | Parâmetros |
| 3 | Extrato por Período | Parâmetros |
| 4 | Ponto Diário | Parâmetros |
| 5 | Inconsistências | Parâmetros |
| 6 | Absenteísmo | Parâmetros |
| 7 | Histórico de Relatórios | Listagem |
| 8 | Relatórios Cadastrais | 15 sub-relatórios |
| 9 | Alterações de Ponto | Parâmetros |
| 10 | Ocorrências | Parâmetros |
| 11 | Assinaturas | Parâmetros |
| 12 | Compensação B. Horas | Parâmetros |
| 13 | Horas Extra | Parâmetros |
| 14 | Turnover | Parâmetros |
| 15 | Local de Trabalho | Parâmetros |
| 16 | Exceções de Ponto | Parâmetros |
| 17 | Afastamentos | Parâmetros |
| 18 | Relatório de Auditoria | Parâmetros |
| 19 | Credenciais | Parâmetros |
| 20 | Hist. de Notificações | Parâmetros |
| 21 | Extrato B. Horas | Parâmetros |

#### Módulos inteiros não cobertos

- **Equipamentos** — gestão de relógios biométricos (parcial: apenas listar/buscar)
- **Config. de Horário** — jornadas, horários, bancos de horas (parcial: apenas escalas)
- **Apuração e Cálculo** — fechamento, cálculo de horas (parcial: apenas consulta)
- **Integração** — importação/exportação
- **Documentos** — gestão documental
- **Fiscalização** — auditoria fiscal
- **Configurações** — parametrização do sistema

> **Próximos passos**: endpoints adicionais (descobertos via DevTools ou pela
> documentação interna da API) podem ser integrados como novas ferramentas em
> `tools/`, seguindo o padrão dos arquivos existentes.

---

## Deploy

### Deploy com Docker (recomendado)

```bash
# Build da imagem
docker build -t rhid-mcp:latest .
# ou via Makefile
make build

# Iniciar
docker compose up -d
# ou via Makefile
make up

# Verificar health check
make health

# Logs
make logs
```

### Deploy no Dokploy (VPS Hostinger)

1. Faça push do repositório para o GitHub
2. No painel Dokploy, crie **Create Application** → tipo **Docker**
3. **Source** → GitHub → selecione o repositório
4. Configure as variáveis de ambiente (ver `DEPLOY.MD`)
5. Aponte o domínio para a porta `8765` com HTTPS via Traefik

### Alternativa: systemd (sem Docker)

```bash
git clone <seu-repo> /opt/rhid-mcp
cd /opt/rhid-mcp
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
# editar .env com as credenciais
cp systemd/rhid-mcp.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now rhid-mcp
```

> 📖 Consulte **[DEPLOY.MD](DEPLOY.MD)** para o guia completo com Docker,
> Dokploy, CI/CD, monitoramento, troubleshooting e segurança.

---

## Configuração no Claude

### Claude Desktop (remoto via VPS)

Edite `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rhid-bhcl": {
      "url": "https://rhid-mcp.seudominio.com/mcp"
    }
  }
}
```

### Claude Code

```bash
claude mcp add rhid-bhcl --transport http https://rhid-mcp.seudominio.com/mcp
```

### Uso local (stdio, sem VPS)

```json
{
  "mcpServers": {
    "rhid-bhcl": {
      "command": "python",
      "args": ["/caminho/para/server.py"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "RHID_LOGIN": "nao-responda@ossbhcl.org.br",
        "RHID_PASSWORD": "sua_senha"
      }
    }
  }
}
```

---

## Adicionando novas ferramentas

Crie um novo arquivo em `tools/` seguindo o padrão:

```python
# tools/minha_nova_funcionalidade.py
from __future__ import annotations
from typing import Any
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from rhid_client import rhid

def register_novas_tools(mcp: FastMCP) -> None:
    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_minha_nova_tool(param: str) -> Any:
        """Descrição da nova ferramenta."""
        return await rhid.get("/algum/endpoint")
```

E registre no `server.py`:
```python
from tools.minha_nova_funcionalidade import register_novas_tools
register_novas_tools(mcp)
```

> 📖 Veja `docs/manual.md` para documentação detalhada de todas as ferramentas,
> DTOs, fluxos de uso e exemplos práticos.