from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from utils.utils_video import video_camara, abrir_camara
from fastapi.responses import FileResponse
import asyncio
import cv2


CAMARAS = {
    "camara_1":"rtsp://admin:tex15cam@192.168.81.70:554/Streaming/channels/101",  # Cámara 1
    "camara_2":"rtsp://admin:tex15cam@192.168.81.71:554/Streaming/channels/101",  # Cámara 2
    "camara_3":"rtsp://admin:tex15cam@192.168.81.72:554/Streaming/channels/101",  # Cámara 3
    "camara_4":"rtsp://admin:tex15cam@192.168.81.73:554/Streaming/channels/101",  # Cámara 4
}


app= FastAPI()
caps= {} #diccionario para guardar las camaras abiertas

for nombre, url in CAMARAS.items():
    caps[nombre]= abrir_camara(url)
    if caps[nombre] is None:
        print(f"⚠️  ADVERTENCIA: No se pudo abrir {nombre}")
    else:
        print(f"✅ {nombre} abierta correctamente")

conexiones ={ #diccionario para guardar las conexiones activas de cada camara
    "conexiones_camara_1":[],
    "conexiones_camara_2":[],
    "conexiones_camara_3":[],
    "conexiones_camara_4":[],
}


@app.on_event("startup")
async def startup_event():
    print("Iniciando servidor...")
    asyncio.create_task(video_camara(caps["camara_1"], conexiones["conexiones_camara_1"]))
    asyncio.create_task(video_camara(caps["camara_2"], conexiones["conexiones_camara_2"]))
    asyncio.create_task(video_camara(caps["camara_3"], conexiones["conexiones_camara_3"]))
    asyncio.create_task(video_camara(caps["camara_4"], conexiones["conexiones_camara_4"]))
    print("4 bucles de video iniciados")


@app.on_event("shutdown")
async def shutdown_event():
    print("Cerrando servidor...")
    for nombre, cap in caps.items():
        if cap and cap.isOpened():
            cap.release()
            print(f"Cámara {nombre} cerrada")
    print("Servidor cerrado")

#@app.get("/")
#async def index():
#    return FileResponse("static/index.html")

@app.get("/camara1")
async def camara1():
    return FileResponse("static/camara1.html")

@app.get("/camara2")
async def camara2():
    return FileResponse("static/camara2.html")

@app.get("/camara3")
async def camara3():
    return FileResponse("static/camara3.html")

@app.get("/camara4")
async def camara4():
    return FileResponse("static/camara4.html")



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

@app.websocket("/ws/camara_2")
async def websocket_camara_2(websocket: WebSocket):
    print("====cliente intentando conectar websocket camara 2====")
    await websocket.accept()
    print("====cliente conectado websocket camara 2====")
    conexiones["conexiones_camara_2"].append(websocket)
    print(f"====cliente agregado a la lista de conexiones activas camara 2, total de usuarios: {len(conexiones["conexiones_camara_2"])}====")
    try:
        while True:
           _= await websocket.receive_text() # _ es una variable que se usa para ignorar el valor que se recibe, es solo para mentener la conexión viva

    except WebSocketDisconnect as e:
        print(f"Cliente desconectado: {e}")            
        conexiones["conexiones_camara_2"].remove(websocket)
    except Exception as e:
        print(f"Error en la conexión de websocket camara 2: {e}")

@app.websocket("/ws/camara_3")
async def websocket_camara_3(websocket: WebSocket):
    print("====cliente intentando conectar websocket camara 3====")
    await websocket.accept()
    print("====cliente conectado websocket camara 3====")
    conexiones["conexiones_camara_3"].append(websocket)
    print(f"====cliente agregado a la lista de conexiones activas camara 3, total de usuarios: {len(conexiones["conexiones_camara_3"])}====")
    try:
        while True:
           _= await websocket.receive_text() # _ es una variable que se usa para ignorar el valor que se recibe, es solo para mentener la conexión viva

    except WebSocketDisconnect as e:
        print(f"Cliente desconectado: {e}")            
        conexiones["conexiones_camara_3"].remove(websocket)
    except Exception as e:
        print(f"Error en la conexión de websocket camara 3: {e}")
        
@app.websocket("/ws/camara_4")
async def websocket_camara_4(websocket: WebSocket):
    print("====cliente intentando conectar websocket camara 4====")
    await websocket.accept()
    print("====cliente conectado websocket camara 4====")
    conexiones["conexiones_camara_4"].append(websocket)
    print(f"====cliente agregado a la lista de conexiones activas camara 4, total de usuarios: {len(conexiones["conexiones_camara_4"])}====")
    try:
        while True:
           _= await websocket.receive_text() # _ es una variable que se usa para ignorar el valor que se recibe, es solo para mentener la conexión viva

    except WebSocketDisconnect as e:
        print(f"Cliente desconectado: {e}")            
        conexiones["conexiones_camara_4"].remove(websocket)
    except Exception as e:
        print(f"Error en la conexión de websocket camara 4: {e}")
        