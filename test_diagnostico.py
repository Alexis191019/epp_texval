import cv2
import time
import socket
from urllib.parse import quote

# ============================================
# CONFIGURACIÓN - MODIFICA ESTOS VALORES
# ============================================
IP = "192.168.81.71"
PUERTO_RTSP = 554
USUARIO = "admin"
CONTRASEÑA = "tex15cam"  # Cambia esto con la contraseña correcta

# ============================================
# DIAGNÓSTICO PASO A PASO
# ============================================

def test_ping_ip(ip):
    """Test 1: Verificar que la IP es accesible"""
    print("\n" + "="*60)
    print("TEST 1: Verificando conectividad con la IP")
    print("="*60)
    try:
        # Intentar hacer ping (Windows)
        import subprocess
        result = subprocess.run(['ping', '-n', '1', ip], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ IP {ip} es accesible")
            return True
        else:
            print(f"❌ IP {ip} NO es accesible")
            return False
    except Exception as e:
        print(f"⚠️  No se pudo hacer ping: {e}")
        print("   (Esto no es crítico, continuamos...)")
        return True  # Continuamos aunque falle el ping

def test_puerto_abierto(ip, puerto):
    """Test 2: Verificar que el puerto está abierto"""
    print("\n" + "="*60)
    print(f"TEST 2: Verificando que el puerto {puerto} está abierto")
    print("="*60)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, puerto))
        sock.close()
        
        if result == 0:
            print(f"✅ Puerto {puerto} está ABIERTO")
            return True
        else:
            print(f"❌ Puerto {puerto} está CERRADO o bloqueado")
            print("   Posibles causas:")
            print("   - Firewall bloqueando el puerto")
            print("   - RTSP deshabilitado en la cámara")
            print("   - Puerto incorrecto")
            return False
    except Exception as e:
        print(f"❌ Error al verificar puerto: {e}")
        return False

def test_credenciales_web(ip, usuario, contraseña):
    """Test 3: Verificar que las credenciales funcionan en la web"""
    print("\n" + "="*60)
    print("TEST 3: Verificando credenciales (acceso web)")
    print("="*60)
    print(f"Usuario: {usuario}")
    print(f"Contraseña: {contraseña}")
    print("\n⚠️  Este test requiere verificación manual:")
    print(f"   1. Abre: http://{ip}")
    print(f"   2. Intenta iniciar sesión con:")
    print(f"      Usuario: {usuario}")
    print(f"      Contraseña: {contraseña}")
    print("   3. ¿Funciona el login? (Sí/No)")
    
    respuesta = input("\n¿Las credenciales funcionan en la web? (s/n): ").lower()
    if respuesta == 's':
        print("✅ Credenciales válidas para acceso web")
        return True
    else:
        print("❌ Credenciales NO válidas")
        print("   ⚠️  IMPORTANTE: Verifica la contraseña exacta")
        return False

def test_rtsp_sin_auth(ip, puerto):
    """Test 4: Intentar conexión RTSP sin autenticación"""
    print("\n" + "="*60)
    print("TEST 4: Intentando RTSP sin autenticación")
    print("="*60)
    
    url = f"rtsp://{ip}:{puerto}/Streaming/channels/101"
    print(f"URL: {url}")
    
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    time.sleep(3)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✅ RTSP funciona SIN autenticación")
            cap.release()
            return True
        else:
            print("⚠️  Conexión abierta pero no se puede leer frame")
    else:
        print("❌ RTSP NO funciona sin autenticación (esperado)")
    
    cap.release()
    return False

def test_rtsp_con_auth(ip, puerto, usuario, contraseña, ruta):
    """Test 5: Intentar RTSP con autenticación"""
    print("\n" + "="*60)
    print("TEST 5: Intentando RTSP con autenticación")
    print("="*60)
    
    # Probar con contraseña normal
    url1 = f"rtsp://{usuario}:{contraseña}@{ip}:{puerto}{ruta}"
    print(f"URL 1 (normal): rtsp://{usuario}:***@{ip}:{puerto}{ruta}")
    
    cap = cv2.VideoCapture(url1, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    time.sleep(5)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✅ ¡ÉXITO! RTSP funciona con estas credenciales")
            print(f"   URL que funcionó: {url1}")
            cap.release()
            return True, url1
        else:
            print("⚠️  Conexión abierta pero no se puede leer frame")
    else:
        print("❌ No funcionó con contraseña normal")
    
    cap.release()
    
    # Probar con contraseña codificada
    contraseña_encoded = quote(contraseña, safe='')
    url2 = f"rtsp://{usuario}:{contraseña_encoded}@{ip}:{puerto}{ruta}"
    print(f"\nURL 2 (codificada): rtsp://{usuario}:***@{ip}:{puerto}{ruta}")
    
    cap = cv2.VideoCapture(url2, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    time.sleep(5)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✅ ¡ÉXITO! RTSP funciona con contraseña codificada")
            print(f"   URL que funcionó: {url2}")
            cap.release()
            return True, url2
        else:
            print("⚠️  Conexión abierta pero no se puede leer frame")
    
    cap.release()
    return False, None

def test_diferentes_rutas(ip, puerto, usuario, contraseña):
    """Test 6: Probar diferentes rutas RTSP"""
    print("\n" + "="*60)
    print("TEST 6: Probando diferentes rutas RTSP")
    print("="*60)
    
    rutas = [
        "/Streaming/channels/101",
        "/Streaming/channels/102",
        "/Streaming/channels/1",
        "/Streaming/Unicast/channels/101",
        "/h264Preview_01_main",
        "/h264Preview_01_sub",
    ]
    
    for ruta in rutas:
        print(f"\nProbando ruta: {ruta}")
        url = f"rtsp://{usuario}:{contraseña}@{ip}:{puerto}{ruta}"
        
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        time.sleep(3)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ ¡ÉXITO! Ruta que funciona: {ruta}")
                print(f"   URL completa: {url}")
                cap.release()
                return True, url
            else:
                print("   ⚠️  Conexión abierta pero sin frame")
        else:
            print("   ❌ No funcionó")
        
        cap.release()
    
    return False, None

# ============================================
# EJECUTAR DIAGNÓSTICO COMPLETO
# ============================================

print("\n" + "="*60)
print("DIAGNÓSTICO COMPLETO DE CONEXIÓN RTSP")
print("="*60)
print(f"\nConfiguración actual:")
print(f"  IP: {IP}")
print(f"  Puerto RTSP: {PUERTO_RTSP}")
print(f"  Usuario: {USUARIO}")
print(f"  Contraseña: {CONTRASEÑA}")
print("\n" + "="*60)

# Ejecutar tests
resultados = {}

resultados['ip'] = test_ping_ip(IP)
resultados['puerto'] = test_puerto_abierto(IP, PUERTO_RTSP)
resultados['credenciales'] = test_credenciales_web(IP, USUARIO, CONTRASEÑA)

if resultados['puerto']:
    resultados['rtsp_sin_auth'] = test_rtsp_sin_auth(IP, PUERTO_RTSP)
    
    if resultados['credenciales']:
        exito, url = test_rtsp_con_auth(IP, PUERTO_RTSP, USUARIO, CONTRASEÑA, "/Streaming/channels/101")
        resultados['rtsp_con_auth'] = exito
        
        if not exito:
            print("\n" + "="*60)
            print("Probando diferentes rutas...")
            print("="*60)
            exito_ruta, url_ruta = test_diferentes_rutas(IP, PUERTO_RTSP, USUARIO, CONTRASEÑA)
            if exito_ruta:
                print(f"\n✅ URL QUE FUNCIONA: {url_ruta}")

# Resumen final
print("\n" + "="*60)
print("RESUMEN DEL DIAGNÓSTICO")
print("="*60)
print(f"IP accesible: {'✅' if resultados.get('ip') else '❌'}")
print(f"Puerto abierto: {'✅' if resultados.get('puerto') else '❌'}")
print(f"Credenciales web: {'✅' if resultados.get('credenciales') else '❌'}")
print(f"RTSP sin auth: {'✅' if resultados.get('rtsp_sin_auth') else '❌'}")
print(f"RTSP con auth: {'✅' if resultados.get('rtsp_con_auth') else '❌'}")

print("\n" + "="*60)
print("RECOMENDACIONES")
print("="*60)

if not resultados.get('puerto'):
    print("❌ PROBLEMA: Puerto 554 está cerrado")
    print("   Solución: Verifica que RTSP esté habilitado en la cámara")
    
if not resultados.get('credenciales'):
    print("❌ PROBLEMA: Credenciales incorrectas")
    print("   Solución: Verifica usuario y contraseña en la interfaz web")
    
if resultados.get('puerto') and resultados.get('credenciales') and not resultados.get('rtsp_con_auth'):
    print("⚠️  PROBLEMA: RTSP no funciona aunque IP y credenciales sean correctas")
    print("   Posibles causas:")
    print("   1. Contraseña incorrecta para RTSP (puede ser diferente a la web)")
    print("   2. Ruta RTSP incorrecta")
    print("   3. Autenticación RTSP configurada incorrectamente")
    print("   4. Usuario sin permisos RTSP")

print("\n")

