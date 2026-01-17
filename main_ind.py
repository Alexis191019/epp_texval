from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from utils.utils_video import video_camara, abrir_camara
from fastapi.responses import FileResponse
import asyncio
import cv2


CAMARAS = {
    "camara_1":"Lavado_test.mp4",  # Cámara 1
}

LINEAS_CAMARAS = {
    "camara_1": ((138, 495), (1753, 462)),
}

app= FastAPI()

caps={} #diccionario para guardar las camaras abiertas

for nombre, path in CAMARAS.items():
    caps[nombre]= abrir_camara(path)
    if caps[nombre] is None:
        print(f"⚠️  ADVERTENCIA: No se pudo abrir {nombre}")
    else:
        print(f"✅ {nombre} abierta correctamente")

conexiones ={ #diccionario para guardar las conexiones activas de cada camara
    "conexiones_camara_1":[],
}


@app.on_event("startup")
async def startup_event():
    print("Iniciando servidor...")
    asyncio.create_task(video_camara(caps["camara_1"], conexiones["conexiones_camara_1"], LINEAS_CAMARAS.get("camara_1")))
    print("bucle de video iniciado")

@app.on_event("shutdown")
async def shutdown_event():
    print("Cerrando servidor...")
    for nombre, cap in caps.items():
        if cap and cap.isOpened():
            cap.release()
            print(f"Cámara {nombre} cerrada")
    print("Servidor cerrado")

@app.get("/")
async def index():
    return FileResponse("static/index.html")

@app.websocket("/ws/camara_1")
async def websocket_camara_1(websocket: WebSocket):
    print("====cliente intentando conectar websocket camara 1====")
    await websocket.accept()
    print("====cliente conectado websocket camara 1====")
    conexiones["conexiones_camara_1"].append(websocket)
    print(f"====cliente agregado a la lista de conexiones activas camara 1, total de usuarios: {len(conexiones["conexiones_camara_1"])}====")
    try:
        while True:
           _= await websocket.receive_text() # _ es una variable que se usa para ignorar el valor que se recibe, es solo para mentener la conexión viva

    except WebSocketDisconnect as e:
        print(f"Cliente desconectado: {e}")            
        conexiones["conexiones_camara_1"].remove(websocket)
    except Exception as e:
        print(f"Error en la conexión de websocket camara 1: {e}")