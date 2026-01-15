import cv2
import time
import os

# Configurar variables de entorno para FFmpeg (ayuda con autenticación)
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp|rtsp_flags;prefer_tcp'

# URL RTSP que funciona (confirmada por diagnóstico)
RTSP_URL = "rtsp://admin:tex15cam@192.168.81.70:554/Streaming/channels/101" #camara uno ip termina en 70 la otra en 71

def leer_camara_rtsp(url):
    print(f"\n{'='*60}")
    print(f"Intentando conectar a: {url}")
    print(f"{'='*60}")
    
    # Método 1: Con parámetros adicionales en la URL
    url_con_opciones = f"{url}?tcp"
    print(f"Probando con opciones TCP: {url_con_opciones}")
    
    cap = cv2.VideoCapture(url_con_opciones, cv2.CAP_FFMPEG)
    
    # Configurar propiedades adicionales
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
    
    print("VideoCapture creado, esperando conexión...")
    time.sleep(5)  # Dar más tiempo para establecer conexión
    
    if not cap.isOpened():
        print("❌ Método 1 falló, probando método alternativo...")
        cap.release()
        
        # Método 2: URL simple sin opciones
        print(f"Probando URL simple: {url}")
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        time.sleep(5)
        
        if not cap.isOpened():
            print("❌ Método 2 también falló")
            return False
    
    # Intentar leer un frame para verificar
    print("Intentando leer primer frame...")
    ret, frame = cap.read()
    
    if not ret:
        print("❌ No se pudo leer el frame")
        cap.release()
        return False
    
    print("✅ ¡Conexión exitosa! Frame leído correctamente")
    print(f"Dimensiones del frame: {frame.shape}")
    
    # Mostrar algunos frames
    print("\nMostrando video (presiona 'q' para salir)...")
    cv2.namedWindow("Hikvision RTSP Stream", cv2.WINDOW_NORMAL)
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: No se pudo leer el fotograma")
            break
        
        cv2.imshow("Hikvision RTSP Stream", frame)
        frame_count += 1
        
        if frame_count % 30 == 0:
            print(f"Frames mostrados: {frame_count}")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return True

# Ejecutar con la URL que funciona
print("Conectando a la cámara Hikvision...")
if leer_camara_rtsp(RTSP_URL):
    print(f"\n✅ ¡Conexión exitosa!")
else:
    print(f"\n❌ No se pudo conectar. Verifica la conexión.")