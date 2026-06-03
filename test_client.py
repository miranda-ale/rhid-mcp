# test_client.py
import asyncio
from rhid_client import rhid

async def main():
    # Testa login + listagem
    empresas = await rhid.get("/company", params={"start": 0, "length": 5})
    print("Empresas:", empresas)

    departamentos = await rhid.get("/department", params={"start": 0, "length": 5})
    print("Departamentos:", departamentos)

    dispositivos = await rhid.get("/device", params={"start": 0, "length": 5})
    print("Dispositivos:", dispositivos)

asyncio.run(main())