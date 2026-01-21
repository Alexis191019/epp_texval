"""
Script para exportar modelo YOLO a TensorRT (optimizado para Jetson Orin)
Ejecutar en la Jetson: python3 exportar_tensorrt.py
"""

from ultralytics import YOLO
import torch

print("=" * 60)
print("EXPORTACIÓN A TENSORRT PARA JETSON ORIN")
print("=" * 60)

# Verificar GPU
if not torch.cuda.is_available():
    print("❌ CUDA no disponible. TensorRT requiere GPU.")
    exit(1)

print(f"\n✅ GPU disponible: {torch.cuda.get_device_name(0)}")
print(f"✅ CUDA versión: {torch.version.cuda}")

# ============================================
# CONFIGURACIÓN - AJUSTA ESTOS VALORES
# ============================================
MODELO_ENTRADA = "modelos/yolov8n.pt"  # Modelo PyTorch de origen
MODELO_SALIDA = "modelos/yolov8n.engine"  # Nombre del archivo TensorRT resultante

# Parámetros de exportación (ajusta según necesites)
CONFIG = {
    "format": "engine",      # Formato TensorRT
    "device": 0,             # GPU 0 (Orin)
    "imgsz": 480,            # Tamaño de imagen (debe coincidir con tu código)
    "half": True,            # FP16 (más rápido que FP32, menos preciso)
    "dynamic": False,        # Entrada fija (más rápido que dynamic=True)
    "workspace": 4,          # Memoria de trabajo en GB
    "int8": False,           # INT8 (más rápido pero requiere calibración)
    # "data": "coco.yaml",   # Dataset para calibración INT8 (descomentar si int8=True)
    # "batch": 1,             # Tamaño de batch (por defecto 1, ajustar si procesas lotes)
}

# ============================================
# EXPORTACIÓN
# ============================================

print(f"\n📦 Cargando modelo: {MODELO_ENTRADA}")
modelo = YOLO(MODELO_ENTRADA)

print("\n🚀 Exportando a TensorRT...")
print("   Configuración:")
for key, value in CONFIG.items():
    print(f"   - {key}: {value}")

print("\n   ⏳ Esto puede tomar varios minutos...")
print("   ⏳ TensorRT optimizará el modelo específicamente para tu Jetson Orin")

try:
    # Exportar
    modelo.export(**CONFIG)
    
    print(f"\n✅ Exportación completada!")
    print(f"   Archivo generado: {MODELO_SALIDA}")
    print("\n📝 PRÓXIMOS PASOS:")
    print("   1. El código ya está configurado para usar TensorRT automáticamente")
    print("   2. Reinicia el servidor: uvicorn main_ind:app --host 0.0.0.0 --port 8000")
    print("   3. Deberías ver: '🚀 Cargando modelo TensorRT...'")
    print("\n💡 Para experimentar con otros parámetros:")
    print("   - Cambia los valores en CONFIG arriba")
    print("   - Ejecuta este script de nuevo")
    print("   - Compara rendimiento")
    
except Exception as e:
    print(f"\n❌ Error durante la exportación: {e}")
    print("\nPosibles causas:")
    print("   - TensorRT no está instalado en JetPack")
    print("   - Falta memoria GPU")
    print("   - Versión incompatible")
    print("\nSolución alternativa: Usar PyTorch optimizado (ya configurado)")

print("\n" + "=" * 60)
