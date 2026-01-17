import cv2
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from utils.utils_computervision import detect, detectar_objetos, linea_deteccion

async def video_camara(cap: cv2.VideoCapture, conexiones_activas: list[WebSocket], linea_coords: tuple=None):
    print("====bucle de video iniciado====")
    loop= asyncio.get_event_loop()
    while True:        
        try:
            if not cap.isOpened():
                print("Error al abrir la cámara, reintentando...")
                continue
            ret, frame= cap.read()
            if linea_coords:
                punto_inicio, punto_fin = linea_coords
                frame = linea_deteccion(frame, punto_inicio, punto_fin)
            if not ret:
                print("Error al leer el frame, reintentando...")
                continue
            try:
                frame_procesado = await loop.run_in_executor(None, detectar_objetos, frame)
                # Verificar que el frame procesado sea válido
                if frame_procesado is not None and frame_procesado.size > 0:
                    frame = frame_procesado
                else:
                    # Si el frame procesado es inválido, usar el original
                    print("⚠️ Frame procesado inválido, usando frame original")
            except Exception as e:
                # Si hay error en la detección, usar el frame original
                print(f"⚠️ Error en detección: {e}, mostrando frame original")
                # frame ya tiene el valor original, no hacer nada

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