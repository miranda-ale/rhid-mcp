# RHID MCP Server — BHCL/Biowise

> **Nota sobre o nome**: O sistema é **RHID** (RHiD / ControlID), e não RHDI.
> A documentação e o código usam exclusivamente `RHID` e `rhid_*` como prefixo das ferramentas.

Servidor MCP para integração com a API **RHID** (ControlID), expondo **32 ferramentas**
que cobrem apuração de ponto, gestão de colaboradores, estrutura organizacional,
dispositivos, escalas e relatórios AFD — para uso no Claude Desktop, Claude Code
e Claude.ai via Projects.

**Versão do sistema**: Control iD v26.6.16.0 — Cliente: BHCL (Beneficência Hospitalar de Cesário Lange)

---

## Cobertura do MCP vs. Sistema Real

### ✅ Coberto — 32 ferramentas (atual)

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

---

## Plano de Expansão — 5 Fases

> **Visão geral**: Expandir das atuais **32 ferramentas** para **~100+**,
> cobrindo todos os 9 módulos do sistema RHID (ControlID v26.6.16.0).

### Fase 1 — CRUDs Imediatos (1-2 dias)

Baseado em **endpoints já confirmados via DevTools** — implementação direta sem necessidade de nova descoberta.

| # | Entidade | Endpoints | Tools | Nomes Sugeridos |
|---|----------|-----------|:-----:|-----------------|
| 1 | **Feriados** | `holiday.svc/{a,c,u,d}` | 4 | `rhid_{criar,listar,atualizar,remover}_feriado` |
| 2 | **Motivos Demissão** | `reasondismissal.svc/{a,c,u,d}` | 4 | `rhid_{criar,listar,atualizar,remover}_motivo_demissao` |
| 3 | **Tipos Justificativa** | `justificationtype.svc/{a,c,u,d}` | 4 | `rhid_{criar,listar,atualizar,remover}_tipo_justificativa` |
| 4 | **Tipos Inconsistência** | `alerttype.svc/{a,c,u,d}` | 4 | `rhid_{criar,listar,atualizar,remover}_tipo_inconsistencia` |
| 5 | **Layouts TXT** | `layouttxt.svc/{a,c,u,d}` | 4 | `rhid_{criar,listar,atualizar,remover}_layout_txt` |

**Impacto:** +20 ferramentas → total **52**

### Fase 2 — CRUDs Estimados (3-5 dias)

Baseado em endpoints **estimados pelo padrão `.svc`** — requer confirmação via DevTools.

| # | Entidade | Endpoint Esperado | Ação Prévia | Tools |
|---|----------|-------------------|-------------|:-----:|
| 6 | **Locais de Trabalho** | `workplace.svc/{a,c,u,d}` | Confirmar via DevTools | 4 |
| 7 | **Fluxos de Aprovação** | `approvalflow.svc/{a,c,u,d}` | Confirmar via DevTools | 4 |
| 8 | **Motivos de Inclusão** | `inclusionreason.svc/{a,c,u,d}` | Confirmar via DevTools | 4 |
| 9 | **Notificações** | `notification.svc/{a,c,u,d}` | Confirmar via DevTools | 4 |

**Impacto:** +16 ferramentas → total **68**

### Fase 3 — Relatórios (1-2 semanas)

Relatórios com parâmetros — requer exploração via DevTools para descobrir os endpoints de cada tipo.

**Ação prévia obrigatória:** Navegar no módulo Relatórios com DevTools aberto, submeter cada formulário e capturar as chamadas de rede.

| Relatório Prioritário | Justificativa |
|-----------------------|---------------|
| **Espelho de Ponto** | Documento legal (Portaria 671) |
| **Cartão de Ponto** | Operacional — alta demanda |
| **Extrato por Período** | Gerencial — alta demanda |
| **Absenteísmo** | Gestão de faltas |
| **Inconsistências** | Relatório de exceção |

**Impacto estimado:** ~12 ferramentas → total **~80**

### Fase 4 — Módulos Novos (2-4 semanas)

Requer exploração completa dos módulos não mapeados atualmente.

| Módulo | Esforço | Dependência |
|--------|:-------:|-------------|
| **Config. de Horário** (escalas, jornadas) | 5 dias | DevTools no módulo |
| **Apuração e Cálculo** (fechamento) | 5 dias | DevTools no módulo |
| **Equipamentos** (gestão completa) | 3 dias | DevTools no módulo |
| **Atribuições em Massa** (wizard) | 3 dias | DevTools nos 3 passos |
| **Faces** (cadastro facial) | 1 dia | Endpoint de solicitação |
| **Relatórios Cadastrais** (15 sub-relatórios) | 2 dias | DevTools em cada sub |

**Impacto estimado:** ~20 ferramentas → total **~100**

### Fase 5 — Integração e Otimização (contínuo)

- Integração com sistemas externos (folha de pagamento, ERP)
- Documentos e gestão documental
- Fiscalização e auditoria fiscal
- Configurações e parametrização do sistema
- Otimização de performance, cache e rate limiting

### Cronograma Recomendado

```
Semana 1  |████████████████████|  Fase 1 (CRUDs imediatos) — +20 tools → 52
Semana 2  |████████████████████|  Fase 2 (CRUDs estimados) — +16 tools → 68
          |                    |  Início: exploração de relatórios (DevTools)
Semana 3  |████████████████████|  Fase 3 (Relatórios) — ~+12 tools → 80
Semana 4  |████████████████████|  Fase 4 (Módulos novos) — ~+20 tools → 100
          |                    |  Início: Config. Horário + Apuração
Semana 5-6|████████████████████|  Fase 4 (continuação) — demais módulos
```

### Métricas de Sucesso

| Marco | Métrica | Alvo |
|-------|---------|:----:|
| Fim da Fase 1 | Tools MCP | 52 |
| Fim da Fase 2 | Tools MCP | 68 |
| Fim da Fase 3 | Tools MCP | ~80 |
| Fim da Fase 4 | Tools MCP | ~100 |
| Cobertura de Cadastros | Submenus cobertos | 15/16 (94%) |
| Cobertura de Relatórios | Tipos cobertos | 25/25 (100%) |
| Cobertura de Módulos | Módulos com cobertura | 9/9 (100%) |

---

## Endpoints Descobertos via DevTools

> A API do RHID (ControlID) expõe dois padrões de endpoints. Abaixo estão os
> **endpoints `.svc`** descobertos através da análise de tráfego de rede do SPA
> (via `performance.getEntriesByType('resource')` no Chrome DevTools).

### Padrão .svc

``` 
https://www.rhid.com.br/v2/api.svc/customerdb/{entidade}.svc/{verbo}[?{parametros}]
```

| Verbo | Operação | Método Provável |
|-------|----------|:---------------:|
| `a` | Listar (DataTables paginado) | `GET` |
| `c` | Criar | `POST` |
| `u` | Atualizar | `PUT` / `POST` |
| `d` | Deletar | `DELETE` / `GET` |

### Endpoints Confirmados (16)

| Endpoint .svc | Entidade | Verbo | Status |
|---------------|----------|-------|--------|
| `company.svc/a` | Empresas | List | ✅ Confirmado |
| `department.svc/a` | Departamentos | List | ✅ Confirmado |
| `costcenter.svc/a` | Centros de Custo | List | ✅ Confirmado |
| `personrole.svc/a` | Cargos | List | ✅ Confirmado |
| `shift.svc/a_escalas/` | Escalas | List | ✅ Confirmado |
| `holiday.svc/a` | Feriados | List | ✅ Confirmado |
| `holiday.svc/d` | Feriados | Delete | ✅ Confirmado |
| `reasondismissal.svc/a` | Motivos Demissão | List | ✅ Confirmado |
| `reasondismissal.svc/d` | Motivos Demissão | Delete | ✅ Confirmado |
| `layouttxt.svc/a` | Layouts TXT | List | ✅ Confirmado |
| `layouttxt.svc/d` | Layouts TXT | Delete | ✅ Confirmado |
| `alerttype.svc/a` | Tipos Inconsistência | List | ✅ Confirmado |
| `alerttype.svc/d` | Tipos Inconsistência | Delete | ✅ Confirmado |
| `justificationtype.svc/a` | Tipos Justificativa | List | ✅ Confirmado |
| `justificationtype.svc/d` | Tipos Justificativa | Delete | ✅ Confirmado |
| `operatorrole.svc/getAdvancedPermissions` | Permissões | — | ✅ Confirmado |

### Endpoints Utilitários Confirmados

| Endpoint | Função |
|----------|--------|
| `util.svc/configUI` | Configurações de UI |
| `util.svc/ultimasmarcacoes` | Últimas marcações (dashboard) |
| `util.svc/dashboardstats/{periodo}` | Estatísticas (7dias, mês, etc) |
| `help.svc/list_videos` | Vídeos de ajuda |
| `login.svc/` | Autenticação |
| `maindb/chatmessage.svc/load` | Chat de suporte (load) |
| `maindb/chatmessage.svc/count` | Chat de suporte (count) |

### Endpoints Estimados (7)

| Endpoint Provável | Entidade | Justificativa |
|-------------------|----------|---------------|
| `workplace.svc/{a,c,u,d}` | Locais de Trabalho | Padrão `.svc` |
| `approvalflow.svc/{a,c,u,d}` | Fluxos de Aprovação | Padrão `.svc` |
| `inclusionreason.svc/{a,c,u,d}` | Motivos de Inclusão | Padrão `.svc` |
| `notification.svc/{a,c,u,d}` | Notificações | Padrão `.svc` |
| `device.svc/{a,c,u,d}` | Equipamentos | `device` já existe via REST |
| `shift.svc/a` ou `schedule.svc/a` | Config. Horário | Escalas, jornadas |
| `overtime.svc/a` | Horas Extras | Relatório específico |

---

## ❌ Gaps conhecidos — não cobertos pelo MCP

### Cadastros (16 submenus — apenas 4 cobertos)

O módulo **Cadastros** possui 16 submenus. O MCP cobre apenas **4** (Colaboradores,
Departamentos, Cargos, Centros de Custo). Faltam:

| # | Submenu | Endpoint | Prioridade |
|---|---------|----------|:----------:|
| 1 | **Faces** | ❌ Não é CRUD | 🟡 Média |
| 2 | **Motivos de Demissão** | ✅ `reasondismissal.svc` | 🔴 Alta |
| 3 | **Feriados** | ✅ `holiday.svc` | 🔴 Alta |
| 4 | **Layouts TXT** | ✅ `layouttxt.svc` | 🔴 Alta |
| 5 | **Tipos de Inconsistência** | ✅ `alerttype.svc` | 🔴 Alta |
| 6 | **Tipos de Justificativa** | ✅ `justificationtype.svc` | 🔴 Alta |
| 7 | **Atribuições em Massa** | ❌ Wizard 3 passos | 🟡 Média |
| 8 | **Locais de Trabalho** | ⬜ Estimado `workplace.svc` | 🟡 Média |
| 9 | **Fluxos de Aprovação** | ⬜ Estimado `approvalflow.svc` | 🟡 Média |
| 10 | **Motivos de Inclusão** | ⬜ Estimado `inclusionreason.svc` | 🟡 Média |
| 11 | **Notificações** | ⬜ Estimado `notification.svc` | 🟡 Média |

### Relatórios (25 tipos — apenas AFD coberto)

O MCP cobre apenas os 4 relatórios AFD (extração de arquivo fiscal). Os **21 tipos
restantes** de relatórios gerenciais e operacionais **não estão disponíveis**:
Espelho de Ponto, Cartão de Ponto, Extrato por Período, Ponto Diário,
Inconsistências, Absenteísmo, Histórico de Relatórios, Relatórios Cadastrais (15 sub),
Alterações de Ponto, Ocorrências, Assinaturas, Compensação B. Horas, Horas Extra,
Turnover, Local de Trabalho, Exceções de Ponto, Afastamentos, Auditoria,
Credenciais, Hist. de Notificações, Extrato B. Horas.

### Módulos inteiros não cobertos

- **Equipamentos** — gestão de relógios biométricos (parcial: apenas listar/buscar)
- **Config. de Horário** — jornadas, horários, bancos de horas (parcial: apenas escalas)
- **Apuração e Cálculo** — fechamento, cálculo de horas (parcial: apenas consulta)
- **Integração** — importação/exportação
- **Documentos** — gestão documental
- **Fiscalização** — auditoria fiscal
- **Configurações** — parametrização do sistema

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

### Padrão REST (Swagger)

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

### Padrão .svc (DevTools — endpoints descobertos)

Para endpoints SPA (`.svc`) descobertos via DevTools, o padrão é análogo
porém com o caminho completo para a rota `.svc`:

```python
# tools/feriados.py
from __future__ import annotations
from typing import Any
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from rhid_client import rhid

_PATH = "/customerdb/holiday.svc"

def register_feriado_tools(mcp: FastMCP) -> None:
    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_feriados() -> Any:
        """Lista todos os feriados cadastrados (endpoint .svc descoberto via DevTools)."""
        return await rhid.get(f"{_PATH}/a")
```

### Registro no server.py

```python
from tools.minha_nova_funcionalidade import register_novas_tools
register_novas_tools(mcp)
```

### Guia de Descoberta de Novos Endpoints

Antes de implementar uma nova entidade, descubra seus endpoints reais via DevTools:

1. Acesse o sistema RHID no navegador (Chrome/Edge) e abra DevTools (F12)
2. Navegue até o módulo desejado
3. No Console, execute:
   ```javascript
   performance.getEntriesByType('resource')
     .filter(e => e.name.includes('.svc'))
     .map(e => ({ url: e.name.split('/v2/api.svc')[1] || e.name }))
   ```
4. Para monitoramento contínuo durante a navegação:
   ```javascript
   (function() {
     window.__rhidSeen = window.__rhidSeen || new Set();
     const observer = new PerformanceObserver((list) => {
       list.getEntries().forEach(entry => {
         if (entry.name.includes('.svc') && !window.__rhidSeen.has(entry.name)) {
           window.__rhidSeen.add(entry.name);
           console.log('🆕 NOVO ENDPOINT:', entry.name.split('/v2/api.svc')[1] || entry.name);
         }
       });
     });
     observer.observe({ entryTypes: ['resource'] });
   })();
   ```

> 📖 Veja `docs/manual.md` para documentação detalhada de todas as ferramentas,
> DTOs, fluxos de uso e exemplos práticos. Veja também o documento de referência
> `docs/plano-expansao.md` (nesta mesma pasta) para o plano completo de expansão.
