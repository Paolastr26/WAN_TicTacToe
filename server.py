# server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Permitir conexiones desde cualquier origen 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista de jugadores conectados 
connected_players = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if len(connected_players) >= 2:
        await websocket.send_text("CERRAR")
        await websocket.close()
        return

    connected_players.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Reenviar a todos los demás jugadores
            for player in connected_players:
                if player != websocket:
                    await player.send_text(data)
    except WebSocketDisconnect:
        connected_players.remove(websocket)
        # Notificar al otro jugador si hay uno
        for player in connected_players:
            await player.send_text("CERRAR")
