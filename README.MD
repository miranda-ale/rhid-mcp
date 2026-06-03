# RHID MCP Server — BHCL/Biowise

Servidor MCP para integração com a API **RHiD** (ControlID), expondo ferramentas
de apuração de ponto, gestão de colaboradores e relatórios para uso no Claude Desktop,
Claude Code e Claude.ai via Projects.

---

## Ferramentas disponíveis

| Tool | Operação | Endpoint |
|------|----------|----------|
| `rhid_apuracao_ponto` | Apuração de jornada por colaborador e período | `GET /apuracao_ponto` |
| `rhid_listar_colaboradores` | Lista paginada de colaboradores | `GET /person` |
| `rhid_listar_colaboradores_com_templates` | Lista com biometria | `GET /person/withtemplates` |
| `rhid_buscar_colaborador` | Colaborador por ID | `GET /person/{id}` |
| `rhid_criar_colaboradores` | Cadastro em lote | `POST /person` |
| `rhid_atualizar_colaborador` | Atualização completa | `PUT /person` |
| `rhid_atualizar_colaboradores_parcial` | Atualização parcial | `PATCH /person` |
| `rhid_remover_colaborador` | Remoção | `DELETE /person/{id}` |
| `rhid_listar_departamentos` | Lista departamentos | `GET /department` |
| `rhid_buscar_departamento` | Depto por ID | `GET /department/{id}` |
| `rhid_criar_departamentos` | Cria departamentos | `POST /department` |
| `rhid_atualizar_departamento` | Atualiza depto | `PUT /department` |
| `rhid_remover_departamento` | Remove depto | `DELETE /department/{id}` |
| `rhid_buscar_centro_custo` | Centro de custo por ID | `GET /costcenters/{id}` |
| `rhid_criar_centros_custo` | Cria centros de custo | `POST /costcenters` |
| `rhid_buscar_cargo` | Cargo por ID | `GET /personroles/{id}` |
| `rhid_criar_cargos` | Cria cargos | `POST /personroles` |
| `rhid_listar_empresas` | Lista empresas/unidades | `GET /company` |
| `rhid_buscar_empresa` | Empresa por ID | `GET /company/{id}` |
| `rhid_relatorio_afd_1510` | AFD Portaria 1510 | `GET /report/afd/download` |
| `rhid_relatorio_afd_671` | AFD Portaria 671 | `GET /report/afd/download671` |
| `rhid_relatorio_afd_coletor_1510` | AFD REP-P 1510 | `GET /report/afd_coletor_marcacao/download` |
| `rhid_relatorio_afd_coletor_671` | AFD REP-P 671 | `GET /report/afd_coletor_marcacao/download671` |
| `rhid_listar_dispositivos` | Lista relógios de ponto | `GET /device` |
| `rhid_buscar_dispositivo` | Dispositivo por ID | `GET /device/{id}` |

> **Endpoints extras** (descobertos via DevTools, não no Swagger) podem ser adicionados
> em novos arquivos dentro de `tools/` seguindo o mesmo padrão.

---

## Deploy na VPS Hostinger

```bash
# 1. Clonar o repositório
git clone <seu-repo> /opt/rhid-mcp
cd /opt/rhid-mcp

# 2. Criar ambiente virtual e instalar dependências
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# 3. Configurar credenciais
cp .env.example .env
nano .env   # preencher RHID_LOGIN e RHID_PASSWORD

# 4. Instalar como serviço systemd
cp rhid-mcp.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now rhid-mcp

# 5. Verificar se está rodando
systemctl status rhid-mcp
curl http://localhost:8765/sse   # deve responder com stream SSE
```

### Expor via Traefik (Dokploy)

No painel Dokploy, crie um novo serviço apontando para `localhost:8765` e configure
o domínio desejado, ex: `rhid-mcp.seudominio.com`. O Traefik cuida do TLS.

---

## Configuração no Claude

### Claude Desktop / Claude Code

Edite `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rhid-bhcl": {
      "url": "https://rhid-mcp.seudominio.com/sse"
    }
  }
}
```

### Uso local (stdio, sem VPS)

```json
{
  "mcpServers": {
    "rhid-bhcl": {
      "command": "python",
      "args": ["/opt/rhid-mcp/server.py"],
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

## Adicionando endpoints extras (descobertos via DevTools)

Crie um novo arquivo em `tools/`, ex: `tools/escalas.py`, seguindo o padrão:

```python
from mcp.server.fastmcp import FastMCP
from rhid_client import rhid

def register_escala_tools(mcp: FastMCP) -> None:
    @mcp.tool(annotations={"readOnlyHint": True})
    async def rhid_listar_escalas() -> dict:
        """Lista todas as escalas de horário."""
        return await rhid.get("/customerdb/shift.svc/a_escalas")
```

E registre no `server.py`:
```python
from tools.escalas import register_escala_tools
register_escala_tools(mcp)
```