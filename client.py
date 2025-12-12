import asyncio
import websockets

async def jugar():
    uri = uri = "ws://192.168.0.11:8080"
    async with websockets.connect(uri) as websocket:
        print("Conectado al servidor 🎮")

        while True:
            mensaje = input("Tu mensaje: ")
            await websocket.send(mensaje)
            print("Enviado ✔️")

            respuesta = await websocket.recv()
            print("Servidor:", respuesta)

asyncio.run(jugar())
