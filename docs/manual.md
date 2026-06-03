# Manual do RHID MCP Server — BHCL/Biowise

Servidor de integração com o **ControlID RHID** (`https://www.rhid.com.br/v2/api.svc`).
Gerencia colaboradores, ponto eletrônico, estrutura organizacional e relatórios AFD.

---

## Padrões globais

| Item | Valor |
|---|---|
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
|---|---|---|
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
|---|---|---|
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
|---|---|---|
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
|---|---|---|
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
|---|---|
| `rhid_listar_departamentos` | GET `/department` (paginado) |
| `rhid_buscar_departamento` | GET `/department/{id}` |
| `rhid_criar_departamentos` | POST — campos: `name`, `idCompany` |
| `rhid_atualizar_departamento` | PUT — campo `id` obrigatório |
| `rhid_remover_departamento` | DELETE ⚠️ |

### Centros de Custo
| Tool | Operação |
|---|---|
| `rhid_buscar_centro_custo` | GET `/costcenters/{id}` |
| `rhid_criar_centros_custo` | POST — campos: `name`, `idCompany` |
| `rhid_atualizar_centro_custo` | PUT — campo `id` obrigatório |
| `rhid_remover_centro_custo` | DELETE ⚠️ |

### Cargos
| Tool | Operação |
|---|---|
| `rhid_buscar_cargo` | GET `/personroles/{id}` |
| `rhid_criar_cargos` | POST — campos: `name`, `idCompany` |
| `rhid_atualizar_cargo` | PUT — campo `id` obrigatório |
| `rhid_remover_cargo` | DELETE ⚠️ |

### Empresas (unidades)
| Tool | Operação |
|---|---|
| `rhid_listar_empresas` | GET `/company` (paginado) |
| `rhid_buscar_empresa` | GET `/company/{id}` |

---

## Relatórios AFD

AFD = Arquivo de Fonte de Dados para fiscalização do MTE.

| Tool | Portaria | Endpoint |
|---|---|---|
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
|---|---|
| `rhid_listar_dispositivos` | GET `/device` — DeviceDTO com status, serial, versão |
| `rhid_buscar_dispositivo` | GET `/device/{id}` — inclui pessoas vinculadas |

---

## Escalas de horário

| Tool | Operação |
|---|---|
| `listar_escalas` | Lista todas as escalas cadastradas |
| `buscar_escala` | Busca por código (ex: `"TT-001"`) |
