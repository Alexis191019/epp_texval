from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from utils.utils_video import video_camara, abrir_camara
from fastapi.responses import FileResponse
import asyncio
import cv2

conexiones_activas = []


app= FastAPI()
cap= abrir_camara(0)
#cap_1= abrir_camara("rtsp://admin:Dlink*123456@192.168.1.64:554/h264Preview_01_main") #para probar con otra camara RTSP



@app.on_event("startup")
async def startup_event():
    print("Iniciando servidor...")
    asyncio.create_task(video_camara(cap, conexiones_activas))
    #asyncio.create_task(video_camara(cap_1, conexiones_activas)) #para probar con otra camara
    print("bucle de video iniciado")


@app.get("/")
async def index():
    return FileResponse("static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("====cliente intentando conectar websocket====")
    await websocket.accept()
    print("====cliente conectado websocket====")
    conexiones_activas.append(websocket)
    print(f"====cliente agregado a la lista de conexiones activas, total de usuarios: {len(conexiones_activas)}====")
    try:
        while True:
           _= await websocket.receive_text() # _ es una variable que se usa para ignorar el valor que se recibe, es solo para mentener la conexión viva

    except WebSocketDisconnect as e:
        print(f"Cliente desconectado: {e}")            
        conexiones_activas.remove(websocket)
    except Exception as e:
        print(f"Error en la conexión de websocket: {e}")