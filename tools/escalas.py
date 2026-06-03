from rhid_client import rhid


def register_escala_tools(mcp):

    @mcp.tool()
    async def listar_escalas() -> dict:
        """Lista todas as escalas de horário cadastradas no RHID."""
        return await rhid.get("/customerdb/shift.svc/a_escalas")

    @mcp.tool()
    async def buscar_escala(codigo: str) -> dict:
        """
        Busca uma escala específica pelo código.
        Args:
            codigo: Código da escala (ex: 'TT-001')
        """
        escalas = await rhid.get("/customerdb/shift.svc/a_escalas")
        # filtrar pelo código — ajustar conforme shape real do response
        for e in escalas.get("data", escalas):
            if e.get("codigo") == codigo or e.get("id") == codigo:
                return e
        return {"erro": f"Escala '{codigo}' não encontrada"}
