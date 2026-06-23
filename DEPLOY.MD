> **Nota sobre o nome**: O sistema integrado é o **RHID** (ControlID), não RHDI.
> Toda a documentação utiliza `RHID` e `rhid_*` como prefixo.

# RHID MCP Server — Guia de Deploy

> Versão: 1.1.0 | Última atualização: Junho 2026

---

## Sumário

1. [Pré-requisitos](#1-pré-requisitos)
2. [Estrutura do projeto](#2-estrutura-do-projeto)
3. [Configuração de variáveis de ambiente](#3-configuração-de-variáveis-de-ambiente)
4. [Deploy local (desenvolvimento)](#4-deploy-local-desenvolvimento)
5. [Deploy com Docker (produção)](#5-deploy-com-docker-produção)
6. [Deploy no Dokploy (VPS Hostinger)](#6-deploy-no-dokploy-vps-hostinger)
7. [Configuração do cliente MCP](#7-configuração-do-cliente-mcp)
8. [Monitoramento e health check](#8-monitoramento-e-health-check)
9. [CI/CD com GitHub Actions](#9-cicd-com-github-actions)
10. [Troubleshooting](#10-troubleshooting)
11. [Segurança](#11-segurança)
12. [Adicionando novos endpoints](#12-adicionando-novos-endpoints)

---

## 1. Pré-requisitos

| Componente       | Versão mínima | Onde                         |
|------------------|---------------|------------------------------|
| Python           | 3.12+         | Máquina local                |
| Docker           | 24+           | VPS ou local                 |
| Node.js          | 18+           | Apenas para MCP Inspector    |
| Git              | qualquer      | Local e VPS                  |
| Dokploy + Traefik| —             | VPS Hostinger (já instalado) |

---

## 2. Estrutura do projeto

```
rhid-mcp/
├── server.py               # Entry point com health check e logging
├── rhid_client.py           # Cliente HTTP (JWT com renovação automática)
├── tools/
│   ├── __init__.py
│   ├── ponto.py             # Apuração de ponto
│   ├── colaboradores.py     # CRUD de Person
│   ├── organizacao.py       # Departamentos, CC, Cargos, Empresas
│   └── relatorios.py        # AFD 1510/671 + Dispositivos
├── Dockerfile               # Build de produção (multi-stage, non-root)
├── docker-compose.yml       # Orquestração com limites e health check
├── .dockerignore
├── .gitignore
├── .env.example             # Template de variáveis
├── requirements.txt
├── Makefile                 # Atalhos para operações comuns
├── rhid-mcp.service         # Alternativa: systemd (sem Docker)
├── DEPLOY.md                # Este arquivo
└── .github/
    └── workflows/
        └── ci.yml           # Pipeline de CI
```

---

## 3. Configuração de variáveis de ambiente

Copie o template e preencha com as credenciais reais:

```bash
cp .env.example .env
```

| Variável         | Obrigatória | Descrição                              | Exemplo                                    |
|------------------|-------------|----------------------------------------|--------------------------------------------|
| `RHID_LOGIN`     | Sim         | E-mail de acesso à API RHID            | `usuario@ossbhcl.org.br`                   |
| `RHID_PASSWORD`  | Sim         | Senha da API RHID                      | `S3nh4_S3gur4`                             |
| `RHID_DOMAIN`    | Não         | Domínio (se multi-tenant)              | *(deixar vazio)*                            |
| `RHID_BASE_URL`  | Não         | URL base da API                        | `https://www.rhid.com.br/v2/api.svc`       |
| `MCP_TRANSPORT`  | Não         | `streamable-http` ou `stdio`           | `streamable-http`                          |
| `MCP_HOST`       | Não         | Bind address                           | `0.0.0.0`                                  |
| `MCP_PORT`       | Não         | Porta do servidor                      | `8765`                                     |
| `LOG_LEVEL`      | Não         | Nível de log (DEBUG, INFO, WARNING)    | `INFO`                                     |

> **IMPORTANTE**: Nunca commitar o `.env` no repositório. Ele está no `.gitignore`.

---

## 4. Deploy local (desenvolvimento)

### 4.1. Setup inicial

```bash
# Clonar o repositório
git clone https://github.com/seu-org/rhid-mcp.git
cd rhid-mcp

# Instalar dependências
make install
# ou manualmente:
python -m venv .venv
.venv/bin/pip install -r requirements.txt   # Linux/macOS
.venv\Scripts\pip install -r requirements.txt  # Windows
```

### 4.2. Testar conexão com a API

```bash
make test
# ou:
python test_client.py
```

Saída esperada: lista de empresas, departamentos e dispositivos sem erros.

### 4.3. Testar com MCP Inspector

```bash
make inspect
# ou:
npx @modelcontextprotocol/inspector python server.py
```

Abre uma UI no browser onde é possível testar cada tool individualmente.

### 4.4. Testar com Claude Desktop (stdio)

Adicione ao `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rhid-bhcl": {
      "command": "python",
      "args": ["C:\\dev\\rhid\\server.py"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "RHID_LOGIN": "seu_email",
        "RHID_PASSWORD": "sua_senha"
      }
    }
  }
}
```

Reinicie o Claude Desktop.

---

## 5. Deploy com Docker (produção)

### 5.1. Build

```bash
make build
# ou:
docker build -t rhid-mcp:latest .
```

A imagem usa:
- **Multi-stage build** — dependências cacheadas em layer separada
- **Usuário não-root** (`mcp:1000`) — princípio de menor privilégio
- **HEALTHCHECK nativo** — Docker monitora automaticamente
- **Labels OCI** — metadados padronizados

### 5.2. Rodar

```bash
make up
# ou:
docker compose up -d
```

### 5.3. Verificar

```bash
# Status do container
docker compose ps

# Health check
make health

# Logs em tempo real
make logs
```

### 5.4. Parar

```bash
make down
```

---

## 6. Deploy no Dokploy (VPS Hostinger)

### 6.1. Preparar repositório

```bash
cd rhid-mcp
git init
git add .
git commit -m "RHID MCP Server v1.0.0"
git remote add origin https://github.com/seu-org/rhid-mcp.git
git push -u origin main
```

### 6.2. Criar aplicação no Dokploy

1. Acessar o painel Dokploy (`https://dokploy.seudominio.com`)
2. **Create Application** → tipo **Docker**
3. **Source** → GitHub → selecionar `rhid-mcp`
4. **Branch** → `main`

### 6.3. Configurar variáveis de ambiente

Na aba **Environment** da aplicação:

```
RHID_LOGIN=nao-responda@ossbhcl.org.br
RHID_PASSWORD=sua_senha_real
RHID_BASE_URL=https://www.rhid.com.br/v2/api.svc
MCP_TRANSPORT=streamable-http
MCP_HOST=0.0.0.0
MCP_PORT=8765
LOG_LEVEL=INFO
```

### 6.4. Configurar domínio

Na aba **Domains**:

| Campo          | Valor                           |
|----------------|---------------------------------|
| Host           | `rhid-mcp.seudominio.com`      |
| Container Port | `8765`                          |
| HTTPS          | Ativado (Traefik gera o cert)   |

### 6.5. Deploy

Clicar em **Deploy** e acompanhar o log de build.

### 6.6. Validar

```bash
# Testar se o endpoint responde
curl -s https://rhid-mcp.seudominio.com/mcp | head -c 200
```

---

## 7. Configuração do cliente MCP

### Claude Desktop (remoto via VPS)

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

### Localização do config no Windows

| Instalação      | Caminho                                                                                 |
|-----------------|-----------------------------------------------------------------------------------------|
| `.exe` direto   | `%APPDATA%\Claude\claude_desktop_config.json`                                           |
| Microsoft Store | `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json` |

Para descobrir automaticamente:

```powershell
Get-ChildItem -Path "$env:APPDATA\Claude","$env:LOCALAPPDATA\Packages\Claude_*\LocalCache\Roaming\Claude" -Filter "claude_desktop_config.json" -Recurse -ErrorAction SilentlyContinue | Select FullName
```

---

## 8. Monitoramento e health check

### Tool `rhid_health_check`

O servidor expõe uma tool MCP que verifica a saúde da conexão com a API:

```
rhid_health_check()
→ {"status": "healthy", "version": "1.0.0", "rhid_api": "connected", "companies_count": 11}
```

### Docker health check

O container reporta seu status automaticamente:

```bash
docker inspect --format='{{.State.Health.Status}}' rhid-mcp
# → healthy | unhealthy | starting
```

### Logs

```bash
# Docker Compose
docker compose logs -f --tail=100

# Dokploy
# Acessar aba "Logs" da aplicação no painel
```

---

## 9. CI/CD com GitHub Actions

O pipeline em `.github/workflows/ci.yml` executa automaticamente em cada push/PR:

1. **Lint** — `ruff check` e `ruff format --check`
2. **Type check** — `pyright` (modo warning)
3. **Build** — constrói a imagem Docker e valida que as 32+ ferramentas estão registradas

Para deploy automático via Dokploy, ative o **Auto Deploy** na configuração da aplicação — o Dokploy faz pull e rebuild automaticamente quando detecta push na branch `main`.

---

## 10. Troubleshooting

### Erro 400 Bad Request nas chamadas

A API RHID exige o header `Authorization: Bearer <token>`. Verifique se o `rhid_client.py` está enviando o prefixo `Bearer`.

### Container "unhealthy"

```bash
# Ver detalhes do health check
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' rhid-mcp
```

Causas comuns: credenciais inválidas no `.env`, API RHID fora do ar, DNS não resolvendo.

### Token expirado / erros intermitentes

O client renova o token automaticamente com margem de 5 minutos. Se os erros persistirem, verifique se as credenciais não foram revogadas no painel do RHID.

### Logs dizem "stdio" mas quero HTTP

Verifique se a variável `MCP_TRANSPORT` está definida como `streamable-http` no ambiente do container (Dokploy → Environment).

### Dispositivo com status "ERRO"

Isso vem da API RHID, não do MCP server. Indica que o relógio de ponto está offline. Verificar conectividade de rede do equipamento físico.

### Datas no formato .NET (`/Date(...)`)

Alguns campos de data da API RHID (ex: `lastConnectionDate` em devices) usam o formato .NET `/Date(timestamp)/`. Para converter:

```python
import re, datetime
raw = "/Date(1780444545000-0300)/"
ms = int(re.search(r"\d+", raw).group())
dt = datetime.datetime.fromtimestamp(ms / 1000)
```

---

## 11. Segurança

### Credenciais

- Variáveis de ambiente via Dokploy (nunca no código)
- `.env` no `.gitignore` (nunca no repositório)
- Rotacionar senha periodicamente no painel RHID

### Container

- Usuário não-root (`mcp:1000`)
- `read_only: true` no docker-compose (filesystem imutável)
- `no-new-privileges` ativado
- Limites de CPU/memória definidos

### Rede

- HTTPS obrigatório via Traefik (TLS automático)
- Porta 8765 exposta apenas internamente ao Docker network
- Traefik faz proxy reverso com certificado Let's Encrypt

### Acesso à API RHID

- O token JWT expira a cada 4 horas
- O client renova automaticamente com margem de segurança
- Nenhuma credencial é exposta nas respostas das tools

---

## 12. Adicionando novos endpoints

Para integrar endpoints descobertos via DevTools (não documentados no Swagger):

### 12.1. Criar o arquivo de tools

```python
# tools/escalas.py
from __future__ import annotations
from typing import Any
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from rhid_client import rhid

_PATH = "/customerdb/shift.svc/a_escalas"

def register_escala_tools(mcp: FastMCP) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def rhid_listar_escalas() -> Any:
        """Lista todas as escalas de horário cadastradas."""
        return await rhid.get(_PATH)
```

### 12.2. Registrar no server.py

```python
from tools.escalas import register_escala_tools
register_escala_tools(mcp)
```

### 12.3. Testar e fazer deploy

```bash
make inspect   # testar no MCP Inspector
git add . && git commit -m "feat: tools de escalas"
git push       # Dokploy faz auto-deploy
```