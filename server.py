# server.py
import os
import asyncio
import websockets

# Conjunto de clientes conectados
clients = set()

async def handler(websocket):
    clients.add(websocket)
    print("📌 Nuevo cliente conectado.")

    try:
        async for message in websocket:
            print(f"Mensaje recibido: {message}")
            # Reenviar el mensaje a todos los demás clientes
            for ws in clients:
                if ws != websocket:
                    await ws.send(message)

    except websockets.ConnectionClosed:
        print("❌ Cliente desconectado.")
    finally:
        clients.remove(websocket)

async def main():
    # Obtener el puerto asignado por Render o usar 8080 por defecto
    PORT = int(os.environ.get("PORT", 8080))
    print(f"🚀 Servidor iniciado. Escuchando en ws://0.0.0.0:{PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()  # Loop infinito para mantener el servidor activo

if __name__ == "__main__":
    asyncio.run(main())
