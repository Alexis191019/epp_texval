import cv2
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from utils.utils_computerviosion import detect, detectar_objetos

async def video_camara(cap: cv2.VideoCapture, conexiones_activas: list[WebSocket]):
    print("====bucle de video iniciado====")
    loop= asyncio.get_event_loop()
    while True:        
        try:
            if not cap.isOpened():
                print("Error al abrir la cámara, reintentando...")
                continue
            ret, frame= cap.read()
            if not ret:
                print("Error al leer el frame, reintentando...")
                continue
            
            frame= await loop.run_in_executor(None, detectar_objetos, frame)
            data = cv2.imencode(".jpg", frame)[1].tobytes()

    

            for conection in conexiones_activas:
                try:
                    await conection.send_bytes(data)

                except WebSocketDisconnect as e:
                    print(f"Cliente desconectado: {e}")
                    conexiones_activas.remove(conection)
                    continue
                except Exception as e:
                    print(f"Error al enviar el frame: {e}")
                    conexiones_activas.remove(conection)
                    continue
                
            await asyncio.sleep(0.03)

        except KeyboardInterrupt:
            print("====bucle de video detenido====")
            break
            
        except Exception as e:
            print(f"Error al leer el frame: {e}")
            continue

def abrir_camara(url_rtsp: str):
    cap= cv2.VideoCapture(url_rtsp)
    if not cap.isOpened():
        print("Error al abrir la cámara")
        return None
    return cap