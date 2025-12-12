# WAN Tic Tac Toe 3D - V3 para Render
import asyncio
import websockets
from tkinter import *
from tkinter import messagebox

# -------------------------------------------------
# VARIABLES GLOBALES
# -------------------------------------------------
SERVER_URL = "wss://wan-tictactoe-1.onrender.com" # tu servidor Render
peer_websocket = None
my_turn = False
running = True

jugadas = [[[0]*4 for _ in range(4)] for _ in range(4)]
C = [[1,1,0],[1,0,1],[0,1,1],[1,0,0],[1,-1,0],[0,0,1],[-1,0,1],[0,1,0],[0,1,-1],
     [0,-1,-1],[0,-1,0],[0,0,-1],[0,0,0]]

X = Y = Z = g = jugador = 0
botones = []
tablero = None
waiting_label = None

# -------------------------------------------------
# FUNCIONES DE RED (WAN via WebSocket)
# -------------------------------------------------
async def connect_to_server():
    global peer_websocket, my_turn, jugador
    try:
        waiting_label.config(text="Conectando al servidor...")
        peer_websocket = await websockets.connect(SERVER_URL)
        waiting_label.config(text="¡Conectado!")
        jugador = 0  # jugador local siempre será X
        my_turn = True
        asyncio.create_task(receive_messages())
    except Exception as e:
        messagebox.showerror("Conexión fallida", f"No se pudo conectar al servidor:\n{e}", parent=tablero)

async def send_move_ws(x, y, z):
    global peer_websocket
    try:
        if peer_websocket:
            await peer_websocket.send(f"{x},{y},{z}")
    except Exception as e:
        if tablero:
            tablero.after(0, lambda: messagebox.showerror("Red", f"Error enviando jugada: {repr(e)}", parent=tablero))

async def receive_messages():
    global my_turn, running
    try:
        async for message in peer_websocket:
            if message == "REINICIAR":
                tablero.after(0, inicio)
                continue
            if message == "CERRAR":
                tablero.after(0, lambda: messagebox.showinfo("Fin", "El rival cerró la partida.", parent=tablero))
                running = False
                tablero.after(0, tablero.destroy)
                break
            x, y, z = map(int, message.split(","))
            tablero.after(0, lambda x=x, y=y, z=z: make_remote_move(x, y, z))
            my_turn = True
            tablero.after(0, enable_buttons)
    except:
        pass

# -------------------------------------------------
# FUNCIONES DEL JUEGO
# -------------------------------------------------
def tablero_lleno():
    for z in range(4):
        for y in range(4):
            for x in range(4):
                if jugadas[z][y][x] == 0:
                    return False
    return True

def fin_partida_dialogo(resultado=""):
    global g
    resp = messagebox.askyesno("Juego terminado", f"{resultado}\n¿Quieres jugar otra vez?", parent=tablero)
    if resp:
        g = 0
        inicio()
        asyncio.create_task(send_move_ws("REINICIAR"))
    else:
        asyncio.create_task(send_move_ws("CERRAR"))
        on_closing()

def crearBoton(valor, i):
    b = Button(tablero, text=valor, width=5, height=1, font=("Helvetica",15),
               command=lambda i=i: botonClick(i), state=DISABLED)
    return b

def enable_buttons():
    for b in botones:
        b['state'] = NORMAL if my_turn and not g else DISABLED

def disable_buttons():
    for b in botones:
        b['state'] = DISABLED

def seguir_o_finalizar():
    global running
    resp = messagebox.askyesno("FINALIZAR", "¿Quieres continuar?", parent=tablero)
    if resp:
        if g:
            inicio()
    else:
        running = False
        try:
            if peer_websocket:
                asyncio.create_task(peer_websocket.close())
        except:
            pass
        tablero.destroy()
    return resp

def botonClick(i):
    global X, Y, Z, g, jugador, my_turn
    if not my_turn or g:
        enable_buttons() if not g else disable_buttons()
        if g:
            seguir_o_finalizar()
        return
    Z = i // 16
    y = i % 16
    Y = y // 4
    X = y % 4
    if jugadas[Z][Y][X]==0:
        jugadas[Z][Y][X] = -1 if jugador==0 else 1
        botones[i].config(text='X' if jugador==0 else 'O', font='arial 15', fg='blue' if jugador==0 else 'red')
        ganador = any(jugada_13(j) for j in range(13))
        asyncio.create_task(send_move_ws(X, Y, Z))
        if ganador:
            g = 1
            disable_buttons()
            Label(tablero, text="¡GANASTE!", font="arial, 20", fg="green").place(x=300,y=50)
            fin_partida_dialogo("GANASTE")
            my_turn = False
            return
        if tablero_lleno():
            g = 1
            disable_buttons()
            Label(tablero, text="¡EMPATE!", font="arial, 20", fg="blue").place(x=300,y=50)
            fin_partida_dialogo("EMPATE")
            my_turn = False
            return
        jugador = not jugador
        my_turn = False
        disable_buttons()
    else:
        Label(tablero, text='Jugada Inválida', font='arial, 20', fg='green').place(x=300, y=5)

def make_remote_move(x, y, z):
    global jugador, g
    i = z*16 + y*4 + x
    if g: return
    if jugadas[z][y][x]==0:
        jugadas[z][y][x] = -1 if jugador!=0 else 1
        botones[i].config(text='O' if jugador==0 else 'X', font='arial 15', fg='red' if jugador!=0 else 'blue')
        ganador = any(jugada_13(j) for j in range(13))
        if ganador:
            g = 1
            disable_buttons()
            Label(tablero, text="¡PERDISTE!", font="arial, 20", fg="red").place(x=300,y=50)
            return
        if tablero_lleno():
            g = 1
            disable_buttons()
            Label(tablero, text="¡EMPATE!", font="arial, 20", fg="blue").place(x=300,y=50)
            return
        jugador = not jugador
    enable_buttons()

def jugada_13(c):
    tz, ty, tx = C[c]
    z1 = Z if tz>0 else -1
    y1 = Y if ty>0 else -1
    x1 = X if tx>0 else -1
    s = 0
    for i in range(4):
        z = Z if z1>=0 else 3-i if tz else i
        y = Y if y1>=0 else 3-i if ty else i
        x = X if x1>=0 else 3-i if tx else i
        s += jugadas[z][y][x]
    if abs(s) < 4:
        return False
    texto_ = 'X' if jugador==0 else 'O'
    for i in range(4):
        z = Z if z1>=0 else 3-i if tz else i
        y = Y if y1>=0 else 3-i if ty else i
        x = X if x1>=0 else 3-i if tx else i
        botones[z*16+y*4+x].config(text=texto_, font='arial 15', fg='yellow', bg='red')
    return True

def inicio():
    global g, X, Y, Z, jugador, my_turn
    for z in range(4):
        for y in range(4):
            for x in range(4):
                jugadas[z][y][x] = 0
                botones[z*16+y*4+x].config(text='', font='arial 15', fg='blue', bg='white')
    X = Y = Z = g = 0
    jugador = 0
    my_turn = True
    Label(tablero, text='Jugador '+str(jugador+1), font='arial, 20', fg='green').place(x=500, y=620)
    enable_buttons()

def on_closing():
    global running
    running = False
    try:
        if peer_websocket:
            asyncio.create_task(peer_websocket.close())
    except:
        pass
    tablero.destroy()

# -------------------------------------------------
# INTERFAZ PRINCIPAL
# -------------------------------------------------
async def start_network_setup():
    global waiting_label, tablero
    tablero = Tk()
    tablero.title('Tic Tac Toe 3D')
    tablero.geometry("1040x720+100+5")
    tablero.resizable(0, 0)
    
    # Crear botones
    for b in range(64):
        botones.append(crearBoton(' ', b))
    contador = 0
    for z in range(3,-1,-1):
        for y in range(4):
            for x in range(4):
                botones[contador].grid(row=y+z*4, column=x+(3-z)*4)
                contador += 1
    
    Button(tablero, text='Exit', width=5, height=1, font=("Helvetica",15),
           command=seguir_o_finalizar).grid(row=0,column=10)
    tablero.protocol("WM_DELETE_WINDOW", on_closing)
    inicio()
    
    waiting_label = Label(tablero, text="Conectando al servidor...", font='arial, 20', fg='magenta')
    waiting_label.place(x=350, y=320)
    
    # Conexión WAN
    asyncio.create_task(connect_to_server())
    
    # Loop principal de Tkinter + asyncio
    while running:
        try:
            tablero.update()
            await asyncio.sleep(0.01)
        except tk.TclError:
            break

# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    asyncio.run(start_network_setup())

