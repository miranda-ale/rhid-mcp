# Manual do RHID MCP Server — BHCL/Biowise

> **Nota sobre o nome**: O sistema é **RHID** (ControlID), e não RHDI.
> Todas as ferramentas usam o prefixo `rhid_*`.

Servidor de integração com o **ControlID RHID** (`https://www.rhid.com.br/v2/api.svc`).
Gerencia colaboradores, ponto eletrônico, estrutura organizacional, dispositivos,
escalas e relatórios AFD.

**Cobertura atual**: 32 ferramentas MCP
**Meta de expansão**: ~100+ ferramentas (plano de 5 fases)
**Sistema**: Control iD v26.6.16.0 — Cliente: BHCL

---

## Sumário

1. [Padrões globais](#padrões-globais)
2. [Fluxo: localizar um colaborador por nome](#fluxo-localizar-um-colaborador-por-nome)
3. [Apuração de ponto](#apuração-de-ponto)
4. [Colaboradores](#colaboradores)
5. [Estrutura organizacional](#estrutura-organizacional)
6. [Relatórios AFD](#relatórios-afd)
7. [Dispositivos biométricos](#dispositivos-biométricos)
8. [Escalas de horário](#escalas-de-horário)
9. [Endpoints DevTools (.svc)](#endpoints-devtools-svc)
10. [Health Check](#health-check)
11. [Gaps de cobertura e plano de expansão](#gaps-de-cobertura-e-plano-de-expansão)

---

## Padrões globais

| Item | Valor |
|------|-------|
| Formato de datas | `DD/MM/YYYY` em todos os parâmetros |
| Paginação padrão | `start=0`, `length=50`; incremente `start` de 50 em 50 |
| Nomes dos colaboradores | Armazenados em **MAIÚSCULAS** na API |
| Chave da listagem de colaboradores | `records` (não `data`, não `results`) |

---

## Fluxo: localizar um colaborador por nome

A API não tem busca por nome — é necessário paginar `rhid_listar_colaboradores` e filtrar localmente.

```
1. Chamar rhid_listar_colaboradores(start=0, length=50)
2. Verificar response["records"] — lista de PersonDTO
3. Se vazio → fim dos registros
4. Senão → filtrar por name.upper() contém o nome buscado
5. Se não encontrado → start += 50 → repetir
```

**PersonDTO — campos principais:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | ID do colaborador (usar em todas as outras tools) |
| `name` | str | Nome completo (MAIÚSCULAS) |
| `cpf` | int | CPF sem formatação |
| `pis` | int | PIS/NIS |
| `registration` | str | Matrícula |
| `idCompany` | int | ID da empresa/unidade |
| `idDepartment` | int | ID do departamento |
| `status` | int | 1=ativo, 0=inativo |

---

## Apuração de ponto

```python
rhid_apuracao_ponto(id_person=<int>, data_ini="DD/MM/YYYY", data_final="DD/MM/YYYY")
```

O tool converte automaticamente DD/MM/YYYY → YYYY-MM-DD antes de enviar à API.

**Retorna `[]` (lista vazia) quando:**
- Colaborador não está vinculado a nenhum dispositivo biométrico (`linkedDeviceIds: []`)
- A empresa não usa controle de ponto eletrônico
- Não há marcações no período informado

Isso **não é erro** — é a resposta legítima da API para esse cenário.

**Estrutura de cada registro diário:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `date` | str | Data do dia (`2026-05-18T00:00:00`) |
| `diasTrabalhados` | int | `1` se trabalhou, `0` se não |
| `diasUteis` | int | `1` se era dia útil no horário |
| `faltaDiaInteiro` | bool | `true` se faltou o dia todo |
| `totalHorasTrabalhadas` | int | Minutos efetivamente trabalhados |
| `isHoliday` | int | `1` se feriado |
| `atrasoEntrada` | int | Minutos de atraso na entrada |
| `horasAusentes` | int | Minutos ausentes no período |
| `saldoBancoFinalDia` | float | Saldo banco de horas ao fim do dia |
| `listAfdtManutencao` | list | Marcações do dia (ver abaixo) |

**Marcações (`listAfdtManutencao`):**

| Campo | Valores | Descrição |
|-------|---------|-----------|
| `_typeEntradaSaida` | `E` / `S` / `D` | Entrada / Saída / Desconto (falta) |
| `_typeClassification` | `J` | Falta justificada |
| `abreviationJustification` | str | Motivo: `Atestado`, `Home Office`, `Declaração de Horas`, etc. |
| `_typeRegister` | `O` / `I` | Original (biométrica) / Inserção manual |
| `diferencaReal` | int | Minutos de diferença em relação ao horário previsto |

**Como identificar faltas:**
```
Falta justificada: _typeEntradaSaida == "D" AND _typeClassification == "J"
Falta sem justificativa: diasUteis == 1 AND diasTrabalhados == 0 AND isHoliday == 0
Atraso: atrasoEntrada > 0
```

---

## Colaboradores

| Tool | Operação | Observação |
|------|----------|------------|
| `rhid_listar_colaboradores` | GET `/person` | Paginar com `start`/`length` |
| `rhid_listar_colaboradores_com_templates` | GET `/person/withtemplates` | Inclui biometria |
| `rhid_buscar_colaborador` | GET `/person/{id}` | Requer `person_id` (int) |
| `rhid_criar_colaboradores` | POST `/person` | Lista de PersonDTO |
| `rhid_atualizar_colaborador` | PUT `/person` | PersonDTO completo com `id` |
| `rhid_atualizar_colaboradores_parcial` | PATCH `/person` | Lista com `id` + campos alterados |
| `rhid_remover_colaborador` | DELETE `/person/{id}` | ⚠️ Destrutivo |

**Criar colaborador — campos mínimos:**
```json
{
  "cpf": 12345678900,
  "name": "NOME COMPLETO",
  "registration": "001",
  "idDepartment": 10,
  "idCompany": 1,
  "status": 1
}
```

---

## Estrutura organizacional

### Departamentos
| Tool | Operação |
|------|----------|
| `rhid_listar_departamentos` | GET `/department` (paginado) |
| `rhid_buscar_departamento` | GET `/department/{id}` |
| `rhid_criar_departamentos` | POST — campos: `name`, `idCompany` |
| `rhid_atualizar_departamento` | PUT — campo `id` obrigatório |
| `rhid_remover_departamento` | DELETE ⚠️ |

### Centros de Custo
| Tool | Operação |
|------|----------|
| `rhid_buscar_centro_custo` | GET `/costcenters/{id}` |
| `rhid_criar_centros_custo` | POST — campos: `name`, `idCompany` |
| `rhid_atualizar_centro_custo` | PUT — campo `id` obrigatório |
| `rhid_remover_centro_custo` | DELETE ⚠️ |

### Cargos
| Tool | Operação |
|------|----------|
| `rhid_buscar_cargo` | GET `/personroles/{id}` |
| `rhid_criar_cargos` | POST — campos: `name`, `idCompany` |
| `rhid_atualizar_cargo` | PUT — campo `id` obrigatório |
| `rhid_remover_cargo` | DELETE ⚠️ |

### Empresas (unidades)
| Tool | Operação |
|------|----------|
| `rhid_listar_empresas` | GET `/company` (paginado) |
| `rhid_buscar_empresa` | GET `/company/{id}` |

---

## Relatórios AFD

AFD = Arquivo de Fonte de Dados para fiscalização do MTE.

| Tool | Portaria | Endpoint |
|------|----------|----------|
| `rhid_relatorio_afd_1510` | 1510 (anterior a 2023) | `/report/afd/download` |
| `rhid_relatorio_afd_671` | 671 (vigente desde 2023) | `/report/afd/download671` |
| `rhid_relatorio_afd_coletor_1510` | 1510 para REP-P | `/report/afd_coletor_marcacao/download` |
| `rhid_relatorio_afd_coletor_671` | 671 para REP-P | `/report/afd_coletor_marcacao/download671` |

**Parâmetros comuns:**
- `id_equipamento` (int, obrigatório): ID do dispositivo
- `data_ini` / `data_final` (str, opcional): período DD/MM/YYYY
- `nsr_inicial` (int, opcional): para extração incremental
- `limit` (int, opcional): limitar registros

---

## Dispositivos biométricos

| Tool | Operação |
|------|----------|
| `rhid_listar_dispositivos` | GET `/device` — DeviceDTO com status, serial, versão |
| `rhid_buscar_dispositivo` | GET `/device/{id}` — inclui pessoas vinculadas |

---

## Escalas de horário

| Tool | Operação |
|------|----------|
| `listar_escalas` | GET `/customerdb/shift.svc/a_escalas` — lista todas as escalas |
| `buscar_escala` | GET `/customerdb/shift.svc/a_escalas` — filtra localmente por código |

**Observação:** Estas ferramentas consultam endpoints descobertos via DevTools
(rota `shift.svc`), não documentados no Swagger oficial da API.

---

## Endpoints DevTools (.svc)

> A API do RHID expõe endpoints **`.svc`** adicionais que não constam no Swagger
> oficial. Estes endpoints foram descobertos via análise do tráfego de rede do SPA
> (frontend) utilizando `Chrome DevTools → performance.getEntriesByType('resource')`.

### Estrutura da URL

```
https://www.rhid.com.br/v2/api.svc/customerdb/{entidade}.svc/{verbo}[?{parametros}]
```

### Tabela de Verbos .svc

| Verbo | Operação | Método HTTP Provável | Descrição |
|-------|----------|:-------------------:|-----------|
| `a` | **A**ll / Listar | `GET` | Lista paginada com parâmetros DataTables |
| `c` | **C**reate | `POST` | Cria um novo registro |
| `u` | **U**pdate | `PUT` / `POST` | Atualiza um registro existente |
| `d` | **D**elete | `DELETE` / `GET` c/ parâmetros | Remove um registro |

### Parâmetros DataTables (verbo `a`)

```json
{
  "draw": 1,
  "columns": [{"data": "nome", "searchable": true}],
  "order": [{"column": 0, "dir": "asc"}],
  "start": 0,
  "length": 10,
  "search": {"value": "", "regex": false}
}
```

### Endpoints Confirmados (16)

| Endpoint | Entidade | Verbo | Status |
|----------|----------|-------|:------:|
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

### Endpoints Estimados (7 — requerem confirmação via DevTools)

| Endpoint Provável | Entidade |
|-------------------|----------|
| `workplace.svc/{a,c,u,d}` | Locais de Trabalho |
| `approvalflow.svc/{a,c,u,d}` | Fluxos de Aprovação |
| `inclusionreason.svc/{a,c,u,d}` | Motivos de Inclusão |
| `notification.svc/{a,c,u,d}` | Notificações |
| `device.svc/{a,c,u,d}` | Equipamentos |
| `shift.svc/a` ou `schedule.svc/a` | Config. Horário |
| `overtime.svc/a` | Horas Extras |

### Guia de Descoberta de Novos Endpoints

#### Método 1: performance.getEntriesByType (recomendado)

1. Abra o DevTools → **Console**
2. Navegue até o módulo desejado (ex: Cadastros → Feriados)
3. Execute:
   ```javascript
   performance.getEntriesByType('resource')
     .filter(e => e.name.includes('.svc'))
     .map(e => ({
       url: e.name.split('/v2/api.svc')[1] || e.name,
       method: e.initiatorType,
       duration: e.duration.toFixed(0) + 'ms'
     }))
   ```

#### Método 2: Monitor Contínuo (sessões longas)

```javascript
(function() {
  if (window.__rhidMonitorActive) return;
  window.__rhidMonitorActive = true;
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
  console.log('✅ Monitor de endpoints ativo! Navegue pelos módulos...');
})();
```

#### Checklist de Exploração por Módulo

| Módulo | Submenus | Status da Exploração |
|--------|----------|----------------------|
| ✅ Cadastros | 16 submenus | **Parcial** — 11 endpoints confirmados via SPA, 5 estimados |
| ⬜ Equipamentos | — | **Não explorado** |
| ⬜ Config. Horário | — | **Não explorado** |
| ⬜ Apuração e Cálculo | — | **Não explorado** |
| ⬜ Relatórios (25 tipos) | 25 submenus | **Não explorado** — requer submissão de formulário |
| ⬜ Integração | — | **Não explorado** |
| ⬜ Documentos | — | **Não explorado** |
| ⬜ Fiscalização | — | **Não explorado** |
| ⬜ Configurações | — | **Não explorado** |

---

## Health Check

| Tool | Descrição |
|------|-----------|
| `rhid_health_check` | Verifica conectividade com a API RHID. Retorna status, versão e nº de empresas. |

Útil para monitoramento pós-deploy e validação de credenciais.

---

## Gaps de cobertura e plano de expansão

### Cobertura Geral

| Métrica | Valor |
|---------|-------|
| Total de módulos do sistema | 9 |
| Módulos com cobertura MCP | 4 (parcial) |
| Submenus de Cadastros | 16 |
| Submenus cobertos | 4 (Colaboradores, Departamentos, Cargos, Centros Custo) |
| Submenus com endpoint descoberto | 11 (via DevTools) |
| Ferramentas MCP atuais | **32** |
| Meta pós-expansão | **~100+** |

### Plano de 5 Fases

O roadmap de expansão está detalhado no `README.MD`. Resumo:

| Fase | Descrição | Prazo | Ferramentas |
|:----:|-----------|:-----:|:-----------:|
| **1** | CRUDs de Feriados, Motivos Demissão, Tipos Justif., Inconsistências, Layouts TXT | 1-2 dias | 52 |
| **2** | CRUDs de Locais Trabalho, Fluxos Aprovação, Motivos Inclusão, Notificações | 3-5 dias | 68 |
| **3** | Relatórios gerenciais (Espelho, Cartão, Extrato, Absenteísmo, etc) | 1-2 sem. | ~80 |
| **4** | Módulos novos (Config. Horário, Apuração, Equipamentos, Atrib. Massa) | 2-4 sem. | ~100 |
| **5** | Integração e otimização contínua | Contínuo | 100+ |

### Prioridades de Implementação

**🔴 Prioridade 1 — Fase 1 (pronto para implementar, endpoints confirmados):**
| # | Entidade | Endpoints |
|---|----------|-----------|
| 1 | Feriados | `holiday.svc/{a,c,u,d}` |
| 2 | Motivos Demissão | `reasondismissal.svc/{a,c,u,d}` |
| 3 | Tipos Justificativa | `justificationtype.svc/{a,c,u,d}` |
| 4 | Tipos Inconsistência | `alerttype.svc/{a,c,u,d}` |
| 5 | Layouts TXT | `layouttxt.svc/{a,c,u,d}` |

**🟡 Prioridade 2 — Fase 2 (confirmar endpoints antes):**
| # | Entidade | Endpoint Esperado |
|---|----------|-------------------|
| 6 | Locais de Trabalho | `workplace.svc/{a,c,u,d}` |
| 7 | Fluxos de Aprovação | `approvalflow.svc/{a,c,u,d}` |
| 8 | Motivos de Inclusão | `inclusionreason.svc/{a,c,u,d}` |
| 9 | Notificações | `notification.svc/{a,c,u,d}` |

**🟢 Prioridade 3 — Fase 3 (requer exploração DevTools):**
| # | Relatório |
|---|-----------|
| 10 | Espelho de Ponto |
| 11 | Cartão de Ponto |
| 12 | Extrato por Período |
| 13-21 | Demais relatórios gerenciais |

### Cadastros (16 submenus — apenas 4 cobertos)

| # | Submenu | Endpoint | Prioridade |
|---|---------|----------|:----------:|
| 1 | **Funcionários** | ✅ REST (coberto) | — |
| 2 | **Empresas** | ✅ REST + SPA (coberto leitura) | ⬜ Baixa |
| 3 | **Departamentos** | ✅ REST + SPA (coberto) | — |
| 4 | **Cargos** | ✅ REST + SPA (coberto) | — |
| 5 | **Centros de Custo** | ✅ REST + SPA (coberto) | — |
| 6 | **Faces** | ❌ Não é CRUD | 🟡 Média |
| 7 | **Motivos de Demissão** | ✅ `reasondismissal.svc` | 🔴 Alta |
| 8 | **Feriados** | ✅ `holiday.svc` | 🔴 Alta |
| 9 | **Layouts TXT** | ✅ `layouttxt.svc` | 🔴 Alta |
| 10 | **Tipos de Inconsistência** | ✅ `alerttype.svc` | 🔴 Alta |
| 11 | **Tipos de Justificativa** | ✅ `justificationtype.svc` | 🔴 Alta |
| 12 | **Atribuições em Massa** | ❌ Wizard 3 passos | 🟡 Média |
| 13 | **Locais de Trabalho** | ⬜ Estimado `workplace.svc` | 🟡 Média |
| 14 | **Fluxos de Aprovação** | ⬜ Estimado `approvalflow.svc` | 🟡 Média |
| 15 | **Motivos de Inclusão** | ⬜ Estimado `inclusionreason.svc` | 🟡 Média |
| 16 | **Notificações** | ⬜ Estimado `notification.svc` | 🟡 Média |

### Relatórios (25 tipos — apenas AFD coberto)

O MCP cobre apenas os 4 relatórios AFD (fiscal). Faltam 21 tipos: Espelho de Ponto,
Cartão de Ponto, Extrato por Período, Ponto Diário, Inconsistências, Absenteísmo,
Histórico de Relatórios, Relatórios Cadastrais (15 sub-relatórios), e outros
relatórios gerenciais.

> Consulte o **README.MD** para o plano de expansão completo com cronograma,
> métricas de sucesso, riscos e mitigações, e guia detalhado de contribuição
> com ferramentas.
