"""
Wrapper HTTP para MCP Server — exponibiliza stdin/stdout via HTTP/SSE.
Usa Server-Sent Events (SSE) para comunicação bidirecional.
"""

import asyncio
import json
import logging
import os
import sys
from collections.abc import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware

# Logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rhid-mcp-http")

app = FastAPI(title="RHID MCP Server", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Processo MCP em background
mcp_process: asyncio.subprocess.Process | None = None
request_queue: asyncio.Queue = asyncio.Queue()
response_queue: asyncio.Queue = asyncio.Queue()


async def start_mcp_process() -> None:
    """Inicia o MCP Server em um processo separado com stdio."""
    global mcp_process

    mcp_process = await asyncio.create_subprocess_exec(
        sys.executable,
        "server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    logger.info("MCP Server iniciado (PID: %s)", mcp_process.pid)

    # Task para ler stderr do MCP
    asyncio.create_task(_relay_mcp_stderr())


async def _relay_mcp_stderr() -> None:
    """Relay stderr do MCP para nossos logs."""
    if not mcp_process or not mcp_process.stderr:
        return

    while True:
        try:
            line = await mcp_process.stderr.readline()
            if not line:
                break
            logger.info("[MCP] %s", line.decode().strip())
        except Exception as e:
            logger.error("Erro ao ler stderr do MCP: %s", e)
            break


async def _mcp_event_loop() -> None:
    """Event loop que proxifica requests/responses do MCP."""
    if not mcp_process or not mcp_process.stdin or not mcp_process.stdout:
        return

    while True:
        try:
            # Aguarda uma requisição
            request_data = await request_queue.get()

            # Envia para MCP via stdin
            mcp_process.stdin.write((json.dumps(request_data) + "\n").encode())
            await mcp_process.stdin.drain()

            # Lê resposta do MCP via stdout
            line = await mcp_process.stdout.readline()
            if not line:
                logger.warning("MCP process fechou stdout")
                break

            response_data = json.loads(line.decode().strip())
            await response_queue.put(response_data)

        except Exception as e:
            logger.error("Erro no event loop do MCP: %s", e)
            break


@app.on_event("startup")
async def startup() -> None:
    """Inicia o MCP e event loop ao subir a aplicação."""
    await start_mcp_process()
    asyncio.create_task(_mcp_event_loop())


@app.on_event("shutdown")
async def shutdown() -> None:
    """Termina o MCP ao desligar a aplicação."""
    if mcp_process:
        mcp_process.terminate()
        try:
            await asyncio.wait_for(mcp_process.wait(), timeout=5)
        except TimeoutError:
            mcp_process.kill()
            await mcp_process.wait()
        logger.info("MCP Server encerrado")


@app.get("/health")
async def health() -> dict:
    """Health check."""
    return {"status": "healthy", "mcp_running": mcp_process is not None}


@app.post("/mcp")
async def mcp_request(request: Request) -> StreamingResponse:
    """
    Proxifica requisição MCP como SSE.
    Recebe JSON do cliente, envia ao MCP via stdin, retorna resposta via SSE.
    """

    async def event_generator() -> AsyncGenerator:
        try:
            # Lê corpo da requisição
            body = await request.body()
            request_data = json.loads(body.decode()) if body else {}

            # Coloca na fila do MCP
            await request_queue.put(request_data)

            # Aguarda resposta
            response_data = await asyncio.wait_for(response_queue.get(), timeout=30)

            # Retorna como SSE
            yield f"data: {json.dumps(response_data)}\n\n"

        except TimeoutError:
            yield f"data: {json.dumps({'error': 'MCP response timeout'})}\n\n"
        except Exception as e:
            logger.exception("Erro em mcp_request")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/mcp")
async def mcp_info() -> dict:
    """Info sobre o servidor MCP."""
    return {
        "name": "rhid-bhcl",
        "version": "1.0.0",
        "status": "running" if mcp_process else "stopped",
    }


if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8765"))

    logger.info("RHID MCP HTTP Server iniciando (host=%s, port=%s)", host, port)

    uvicorn.run(app, host=host, port=port, log_level="info")
