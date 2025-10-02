#!/usr/bin/env python3

"""
Programa básico para leer una imagen de la cámara OAK-4D R9
Versión simplificada compatible con DepthAI 3.0+
Cámara detectada: Luxonis KalamaP OAK4-D R9 (Serial: 2533390442)
IP: 192.168.200.126
"""

import cv2
import depthai as dai
import numpy as np

def capture_image_simple():
    """
    Captura una imagen desde la cámara OAK-4D R9 usando método simplificado
    """
    print("Buscando dispositivos DepthAI...")
    
    # Listar dispositivos disponibles
    found_devices = dai.Device.getAllAvailableDevices()
    if len(found_devices) == 0:
        print("❌ No se encontraron dispositivos DepthAI")
        print("\nVerifica:")
        print("1. Que la cámara OAK-4D esté encendida")
        print("2. La conexión de red (IP: 192.168.200.126)")
        print("3. Que estés en la misma red que la cámara")
        return
    
    print(f"✓ Se encontraron {len(found_devices)} dispositivos:")
    for i, device in enumerate(found_devices):
        device_info = str(device)
        print(f"  {i+1}. {device_info}")
    
    # Usar el primer dispositivo encontrado
    target_device = found_devices[0]
    
    try:
        # Conectar al dispositivo de forma simple
        with dai.Device() as device:
            print(f"\n🎥 Conectado exitosamente a la cámara OAK-4D R9")
            print("=== INICIANDO CAPTURA ===")
            
            # Obtener las colas disponibles del dispositivo
            q_list = device.getQueueEvents()
            print(f"Colas disponibles: {len(q_list)}")
            
            # Intentar obtener frames usando diferentes métodos
            print("Intentando obtener imagen...")
            
            # Método 1: Intentar crear un pipeline simple
            try:
                pipeline = dai.Pipeline()
                
                # Crear cámara RGB
                cam_rgb = pipeline.createColorCamera()
                cam_rgb.setPreviewSize(640, 480)
                cam_rgb.setInterleaved(False)
                
                # Crear salida
                xout_rgb = pipeline.createXLinkOut()
                xout_rgb.setStreamName("rgb")
                cam_rgb.preview.link(xout_rgb.input)
                
                # Iniciar pipeline
                device.startPipeline(pipeline)
                q_rgb = device.getOutputQueue("rgb")
                
                print("✓ Pipeline iniciado correctamente")
                print("Presiona 'q' para salir, 's' para capturar imagen")
                
                capture_count = 0
                
                while True:
                    # Obtener frame
                    in_rgb = q_rgb.get()
                    frame = in_rgb.getCvFrame()
                    
                    # Agregar información
                    cv2.putText(frame, "OAK-4D R9 - Serial: 2533390442", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "IP: 192.168.200.126", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, f"Capturas: {capture_count}", (10, 110), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Mostrar resolución
                    height, width = frame.shape[:2]
                    cv2.putText(frame, f"Resolucion: {width}x{height}", (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Instrucciones
                    cv2.putText(frame, "Presiona 'q'=salir, 's'=capturar", 
                               (10, frame.shape[0] - 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Mostrar imagen
                    cv2.imshow("OAK-4D R9 - Captura en Vivo", frame)
                    
                    # Procesar teclas
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord('q'):
                        print("👋 Saliendo...")
                        break
                    elif key == ord('s'):
                        # Capturar imagen
                        import time
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"captura_oak4d_{timestamp}.jpg"
                        
                        # Guardar con alta calidad
                        cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        capture_count += 1
                        print(f"📸 Imagen {capture_count} guardada: {filename}")
                        
            except Exception as pipeline_error:
                print(f"Error en pipeline: {pipeline_error}")
                
    except Exception as e:
        print(f"❌ Error al conectar con la cámara: {e}")
        print(f"Tipo de error: {type(e).__name__}")
        print("\nPosibles soluciones:")
        print("1. Verifica que la cámara OAK-4D esté encendida")
        print("2. Verifica la conexión de red")
        print("3. Reinicia la cámara")
        print("4. Verifica que no haya firewall bloqueando")
    
    finally:
        cv2.destroyAllWindows()
        print("✅ Programa finalizado")

def test_connection():
    """
    Prueba básica de conexión
    """
    print("=== PRUEBA DE CONEXIÓN ===")
    
    try:
        # Verificar versión de DepthAI
        print(f"Versión DepthAI: {dai.__version__}")
        
        # Listar dispositivos
        devices = dai.Device.getAllAvailableDevices()
        print(f"Dispositivos encontrados: {len(devices)}")
        
        for i, device in enumerate(devices):
            print(f"Dispositivo {i+1}: {device}")
        
        if len(devices) > 0:
            print("✓ Conexión disponible")
            return True
        else:
            print("❌ No hay dispositivos conectados")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de conexión: {e}")
        return False

if __name__ == "__main__":
    print("=== Programa de Captura OAK-4D R9 ===")
    print("Versión simplificada para DepthAI 3.0+")
    print("Cámara: Luxonis KalamaP OAK4-D R9")
    print("Serial: 2533390442")
    print("IP: 192.168.200.126")
    print("=" * 45)
    
    # Probar conexión primero
    if test_connection():
        print("\n🚀 Iniciando captura...")
        capture_image_simple()
    else:
        print("\n❌ No se puede iniciar la captura sin conexión")