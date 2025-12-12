# server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI()

# Permitir conexiones desde cualquier origen (para pruebas WAN)
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
    
    # Limitar a 2 jugadores
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
        # Notificar al otro jugador que el oponente cerró
        for player in connected_players:
            await player.send_text("CERRAR")

# -------------------------------------------------
# Ejecutar servidor con el puerto asignado por Render
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render define la variable PORT
    uvicorn.run("server:app", host="0.0.0.0", port=port, log_level="info")
