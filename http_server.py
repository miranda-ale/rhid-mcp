"""
HTTP wrapper para o RHID MCP Server.
Usa o transport nativo streamable-http do FastMCP com autenticação por API key.
"""

import json
import logging
import os
import secrets

import uvicorn

from server import mcp  # FastMCP instance com todas as tools registradas

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rhid-mcp-http")

_API_KEY = os.getenv("MCP_API_KEY", "")


class _ApiKeyMiddleware:
    """Pure-ASGI middleware — não bufferiza streaming responses (SSE/MCP)."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = scope.get("path", "")

        if path == "/health":
            await self._health(send)
            return

        if not _API_KEY:
            logger.warning("MCP_API_KEY não configurada — acesso bloqueado")
            await self._json(send, 503, {"error": "server misconfigured"})
            return

        headers = {k.lower(): v for k, v in scope.get("headers", [])}
        auth = headers.get(b"authorization", b"").decode()
        token = auth.removeprefix("Bearer ").strip()

        if not secrets.compare_digest(token, _API_KEY):
            logger.warning(
                "Acesso não autorizado: %s %s",
                scope.get("method"),
                path,
            )
            await self._json(send, 401, {"error": "unauthorized"})
            return

        await self.app(scope, receive, send)

    @staticmethod
    async def _health(send) -> None:
        payload = b'{"status":"healthy"}'
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"application/json"],
                [b"content-length", str(len(payload)).encode()],
            ],
        })
        await send({"type": "http.response.body", "body": payload})

    @staticmethod
    async def _json(send, status: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", b"application/json"],
                [b"content-length", str(len(payload)).encode()],
            ],
        })
        await send({"type": "http.response.body", "body": payload})


# FastMCP expõe /mcp com o transport streamable-http nativo
app = _ApiKeyMiddleware(mcp.streamable_http_app())


if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8765"))
    logger.info("RHID MCP HTTP Server iniciando (host=%s, port=%s)", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")
