# server.py
import asyncio
import websockets

clients = set()

async def handler(websocket):
    clients.add(websocket)
    print("Nuevo cliente conectado.")

    try:
        async for message in websocket:
            print("Mensaje recibido:", message)

            # reenviar el mensaje a TODOS los demás clientes
            for ws in clients:
                if ws != websocket:
                    await ws.send(message)

    except:
        print("Cliente desconectado.")

    finally:
        clients.remove(websocket)


async def main():
    print("Servidor iniciado en ws://localhost:8080")
    async with websockets.serve(handler, "0.0.0.0", 8080):
        await asyncio.Future()  # loop infinito


asyncio.run(main())
