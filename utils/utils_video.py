import cv2
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import time
from utils.utils_computervision import detect, detectar_objetos, linea_deteccion

async def video_camara(cap: cv2.VideoCapture, conexiones_activas: list[WebSocket], linea_coords: tuple=None):
    print("====bucle de video iniciado====")
    loop= asyncio.get_event_loop()
    
    # Optimización: Procesar solo cada N frames (skip frames)
    # Con 4 cámaras, procesar cada 3 frames = ~10 fps de detección por cámara
    contador_frames = 0
    SKIP_FRAMES = 3  # Procesar cada 3 frames (reducir carga con múltiples cámaras)
    
    # Optimización: Cachear último frame procesado para reutilizar
    ultimo_frame_procesado = None
    
    # Optimización: Reducir resolución para transmisión más rápida
    RESOLUCION_MAXIMA = 960  # Reducido de 1280 para menos datos

    # Variables para cálculo de FPS (promedio móvil)
    ultimo_tiempo = time.time()
    fps_actual = 0.0
    
    while True:        
        try:
            if not cap.isOpened():
                print("Error al abrir la cámara, reintentando...")
                continue
            ret, frame= cap.read()
            if not ret:
                print("Error al leer el frame, reintentando...")
                continue
            
            # Optimización: Reducir resolución para transmisión
            altura, ancho = frame.shape[:2]
            if ancho > RESOLUCION_MAXIMA:
                escala = RESOLUCION_MAXIMA / ancho
                nuevo_ancho = RESOLUCION_MAXIMA
                nueva_altura = int(altura * escala)
                frame = cv2.resize(frame, (nuevo_ancho, nueva_altura))
            
            if linea_coords:
                punto_inicio, punto_fin = linea_coords
                frame = linea_deteccion(frame, punto_inicio, punto_fin)
            
            # Optimización: Procesar solo cada N frames
            contador_frames += 1
            if contador_frames % SKIP_FRAMES == 0:
                try:
                    frame_procesado = await loop.run_in_executor(None, detectar_objetos, frame)
                    # Verificar que el frame procesado sea válido
                    if frame_procesado is not None and frame_procesado.size > 0:
                        frame = frame_procesado
                        ultimo_frame_procesado = frame.copy()  # Guardar para reutilizar (ya incluye línea y detecciones)
                except Exception as e:
                    # Si hay error en la detección, usar el último procesado o el frame original
                    if ultimo_frame_procesado is not None:
                        frame = ultimo_frame_procesado.copy()  # Reutilizar último frame procesado
                    print(f"⚠️ Error en detección: {e}, usando frame cacheado")
            else:
                # Si no procesamos este frame, reutilizar el último procesado si existe
                # Esto mantiene las detecciones visibles mientras reduce carga de procesamiento
                if ultimo_frame_procesado is not None:
                    frame = ultimo_frame_procesado.copy()  # Reutilizar (ya tiene línea y detecciones)

            # Calcular FPS (frames por segundo)
            ahora = time.time()
            dt = ahora - ultimo_tiempo
            ultimo_tiempo = ahora
            if dt > 0:
                # Promedio móvil exponencial para suavizar
                fps_instantaneo = 1.0 / dt
                fps_actual = 0.9 * fps_actual + 0.1 * fps_instantaneo if fps_actual > 0 else fps_instantaneo

            # Dibujar FPS en la esquina superior izquierda
            texto_fps = f"FPS: {fps_actual:.1f}"
            cv2.putText(
                frame,
                texto_fps,
                (10, 30),  # posición (x, y)
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,       # tamaño de fuente
                (0, 255, 0),  # color (B, G, R)
                2,
                cv2.LINE_AA,
            )

            # Optimización: Reducir calidad JPEG para transmisión más rápida
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 60]  # Calidad 60 (más bajo = más rápido)
            data = cv2.imencode(".jpg", frame, encode_params)[1].tobytes()

    

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
                
            # Optimización: Ajustar sleep según procesamiento y número de conexiones
            # Con múltiples cámaras, necesitamos más tiempo entre frames
            if len(conexiones_activas) == 0:
                await asyncio.sleep(0.1)  # Más lento si no hay clientes
            else:
                # Ajustar según carga: más tiempo si hay muchas conexiones
                sleep_time = 0.033 + (len(conexiones_activas) * 0.01)  # ~30fps base + penalización
                await asyncio.sleep(min(sleep_time, 0.1))  # Máximo 0.1 segundos

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