from ultralytics import YOLO
import cv2
import supervision as sv
import torch
import os

# Detectar automáticamente si hay GPU disponible
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"🔧 Dispositivo detectado: {device}")

# Bandera para saber si estamos usando TensorRT o PyTorch
USANDO_TENSORRT = False

# Intentar cargar modelo TensorRT primero (más rápido); si no existe, usar PyTorch (.pt)
# NOTA: ajusta el nombre del archivo .engine al que realmente tienes en la carpeta modelos
engine_path = "modelos/yolo26n.engine"  # tu modelo TensorRT
pt_path = "modelos/yolov8n.pt"          # modelo PyTorch de respaldo

if os.path.exists(engine_path):
    print("🚀 Cargando modelo TensorRT (optimizado para Jetson)...")
    try:
        modelo = YOLO(engine_path)
        USANDO_TENSORRT = True
        print("✅ Modelo TensorRT cargado")
    except Exception as e:
        print(f"❌ No se pudo cargar TensorRT: {e}")
        print("📦 Recurriendo a modelo PyTorch (.pt)...")
        modelo = YOLO(pt_path)
        USANDO_TENSORRT = False
        if device == 'cuda':
            modelo.to(device)
            print("✅ Modelo PyTorch cargado en GPU")
        else:
            print("⚠️  GPU no disponible, usando CPU")
else:
    print("📦 Cargando modelo PyTorch (.pt)...")
    modelo = YOLO(pt_path)
    USANDO_TENSORRT = False
    # Mover el modelo a GPU si está disponible (solo válido para modelos PyTorch)
    if device == 'cuda':
        modelo.to(device)
        print("✅ Modelo PyTorch cargado en GPU")
    else:
        print("⚠️  GPU no disponible, usando CPU")

tracker = sv.ByteTrack()
box_annotator= sv.BoxAnnotator()
label_annotator= sv.LabelAnnotator()

def detectar_objetos(frame, modelo= modelo):
    # Optimización: Reducir tamaño de imagen para YOLO (más rápido)
    # Guardar tamaño original para escalar detecciones después
    altura_original, ancho_original = frame.shape[:2]
    
    # Optimización agresiva: Reducir a máximo 480px para procesamiento más rápido
    # Con 4 cámaras, necesitamos procesar más rápido
    TAMANO_PROCESAMIENTO = 480
    escala = min(TAMANO_PROCESAMIENTO / ancho_original, TAMANO_PROCESAMIENTO / altura_original)
    if escala < 1.0:
        nuevo_ancho = int(ancho_original * escala)
        nueva_altura = int(altura_original * escala)
        frame_pequeño = cv2.resize(frame, (nuevo_ancho, nueva_altura), interpolation=cv2.INTER_LINEAR)
    else:
        frame_pequeño = frame
        escala = 1.0
    
    # CRÍTICO: Asegurar que el modelo y los datos estén en GPU
    # Ultralytics puede hacer transferencias innecesarias CPU-GPU
    # Especificar device explícitamente y forzar GPU
    resultados= modelo.predict(
        frame_pequeño, 
        conf=0.50, 
        device=device,  # Asegurar que use GPU
        imgsz=480,  # Reducido de 640 a 480 para más velocidad
        verbose=False,  # Desactivar logs para mejor rendimiento
        half=False,  # No usar FP16 en Jetson (puede ser más lento)
        agnostic_nms=False,  # NMS normal (más rápido que agnostic)
        stream=False  # Procesar de forma síncrona (más eficiente para Jetson)
    )[0]
    
    detections = sv.Detections.from_ultralytics(resultados)
    
    # Escalar detecciones de vuelta al tamaño original si se redujo
    if escala < 1.0:
        detections.xyxy = detections.xyxy / escala
        # También escalar los puntos centrales si existen
        if hasattr(detections, 'xyxy') and len(detections.xyxy) > 0:
            # Las coordenadas ya están escaladas correctamente con xyxy
            pass
    
    detections = tracker.update_with_detections(detections)
    
    labels = [
        f"#{tracker_id} {class_name}"
        for class_name, tracker_id
        in zip(detections.data["class_name"], detections.tracker_id)
    ]
    
    annotated_frame = box_annotator.annotate(
        scene=frame.copy(), detections=detections)
    annotated_frame = label_annotator.annotate(
        scene=annotated_frame, detections=detections, labels=labels)
    return annotated_frame

def detect(frame, modelo= modelo):
    resultados= modelo.predict(frame, conf=0.5, device=device)[0]
    detections= resultados.plot()
    return detections

def linea_deteccion(frame, punto_inicio:tuple[int, int], punto_fin:tuple[int, int]):
    linea= cv2.line(frame, punto_inicio, punto_fin, (0, 0, 255), 2)
    return linea
