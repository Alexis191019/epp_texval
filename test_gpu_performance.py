"""
Script de diagnóstico para verificar rendimiento GPU en Jetson
"""
import torch
import cv2
import time
from ultralytics import YOLO
import numpy as np

print("=" * 60)
print("DIAGNÓSTICO DE RENDIMIENTO GPU - JETSON")
print("=" * 60)

# 1. Verificar GPU
print("\n1. VERIFICACIÓN DE GPU:")
print(f"   CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   Dispositivo: {torch.cuda.get_device_name(0)}")
    print(f"   CUDA versión: {torch.version.cuda}")
    print(f"   PyTorch versión: {torch.__version__}")
    
    # Verificar memoria GPU
    print(f"\n   Memoria GPU:")
    print(f"   - Total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    print(f"   - Reservada: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
    print(f"   - En uso: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")

# 2. Cargar modelo
print("\n2. CARGA DE MODELO:")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
modelo = YOLO("modelos/yolov8n.pt")
if device == 'cuda':
    modelo.to(device)
    print(f"   ✅ Modelo movido a {device}")

# 3. Verificar dónde está el modelo realmente
print("\n3. VERIFICACIÓN DE UBICACIÓN DEL MODELO:")
try:
    # Intentar acceder a los parámetros del modelo
    primer_param = next(modelo.model.parameters())
    print(f"   Ubicación del primer parámetro: {primer_param.device}")
    if primer_param.device.type == 'cuda':
        print("   ✅ Modelo está en GPU")
    else:
        print("   ⚠️  Modelo está en CPU (PROBLEMA!)")
except Exception as e:
    print(f"   ⚠️  No se pudo verificar: {e}")

# 4. Crear frame de prueba
print("\n4. PRUEBA DE INFERENCIA:")
frame_prueba = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
print(f"   Frame de prueba: {frame_prueba.shape}")

# 5. Prueba de velocidad
print("\n5. BENCHMARK DE VELOCIDAD:")
num_pruebas = 10
tiempos = []

# Calentar GPU
print("   Calentando GPU...")
for _ in range(3):
    _ = modelo.predict(frame_prueba, device=device, verbose=False, imgsz=480)

# Medir tiempos
print(f"   Ejecutando {num_pruebas} inferencias...")
for i in range(num_pruebas):
    inicio = time.time()
    resultados = modelo.predict(frame_prueba, device=device, verbose=False, imgsz=480, conf=0.5)
    fin = time.time()
    tiempo = (fin - inicio) * 1000  # Convertir a ms
    tiempos.append(tiempo)
    print(f"   Inferencia {i+1}: {tiempo:.2f} ms")

tiempo_promedio = sum(tiempos) / len(tiempos)
tiempo_min = min(tiempos)
tiempo_max = max(tiempos)

print(f"\n   RESULTADOS:")
print(f"   - Promedio: {tiempo_promedio:.2f} ms")
print(f"   - Mínimo: {tiempo_min:.2f} ms")
print(f"   - Máximo: {tiempo_max:.2f} ms")
print(f"   - FPS estimado: {1000/tiempo_promedio:.1f}")

# 6. Verificar uso de GPU durante inferencia
print("\n6. VERIFICACIÓN DE USO DE GPU:")
print("   Ejecuta 'nvidia-smi' en otra terminal mientras corre este script")
print("   para verificar que la GPU se está usando realmente")

# 7. Comparación CPU vs GPU (si es posible)
if torch.cuda.is_available():
    print("\n7. COMPARACIÓN CPU vs GPU:")
    print("   Probando CPU...")
    modelo_cpu = YOLO("modelos/yolov8n.pt")
    modelo_cpu.to('cpu')
    
    tiempos_cpu = []
    for i in range(5):
        inicio = time.time()
        _ = modelo_cpu.predict(frame_prueba, device='cpu', verbose=False, imgsz=480, conf=0.5)
        fin = time.time()
        tiempos_cpu.append((fin - inicio) * 1000)
    
    tiempo_cpu_promedio = sum(tiempos_cpu) / len(tiempos_cpu)
    print(f"   CPU promedio: {tiempo_cpu_promedio:.2f} ms")
    print(f"   GPU promedio: {tiempo_promedio:.2f} ms")
    
    if tiempo_cpu_promedio < tiempo_promedio * 1.5:
        print("   ⚠️  ADVERTENCIA: GPU no es significativamente más rápida que CPU!")
        print("   Esto indica que puede haber un problema de configuración.")
    else:
        aceleracion = tiempo_cpu_promedio / tiempo_promedio
        print(f"   ✅ GPU es {aceleracion:.2f}x más rápida que CPU")

print("\n" + "=" * 60)
print("FIN DEL DIAGNÓSTICO")
print("=" * 60)
