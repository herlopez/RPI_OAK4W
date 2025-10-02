#!/usr/bin/env python3

"""
Programa básico para leer una imagen de la cámara OAK-4D R9
Compatible con DepthAI 3.0+
Cámara detectada: Luxonis KalamaP OAK4-D R9 (Serial: 2533390442)
IP: 192.168.200.126
"""

import cv2
import depthai as dai
import numpy as np

def capture_image():
    """
    Captura una imagen desde la cámara OAK-4D R9
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
        device_id = device.mxid if hasattr(device, 'mxid') else str(device)
        device_name = device.name if hasattr(device, 'name') else "Dispositivo DepthAI"
        print(f"  {i+1}. {device_id} - {device_name}")
    
    # Buscar nuestro dispositivo específico
    target_device = None
    for device in found_devices:
        device_id = device.mxid if hasattr(device, 'mxid') else str(device)
        if "2533390442" in device_id:
            target_device = device
            print(f"✓ Cámara OAK-4D R9 encontrada: {device_id}")
            break
    
    # Si no encontramos el específico, usar el primero
    if target_device is None:
        target_device = found_devices[0]
        device_id = target_device.mxid if hasattr(target_device, 'mxid') else str(target_device)
        print(f"Usando primer dispositivo disponible: {device_id}")
    
    # Crear pipeline simple
    pipeline = dai.Pipeline()
    
    # Crear nodo de cámara (usando la nueva API)
    cam = pipeline.create(dai.node.Camera)
    cam.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
    cam.setFps(30)
    
    # Crear salida para stream de video
    videoOut = pipeline.createXLinkOut()
    videoOut.setStreamName("video")
    
    # Conectar cámara a salida
    cam.video.link(videoOut.input)
    
    # Conectar al dispositivo
    try:
        with dai.Device(pipeline, target_device) as device:
            device_id = device.getMxId() if hasattr(device, 'getMxId') else "Dispositivo Conectado"
            print(f"\n🎥 Conectado a: {device_id}")
            print("=== CÁMARA OAK-4D R9 ACTIVA ===")
            print("Controles:")
            print("- Presiona 'q' para salir")
            print("- Presiona 's' para capturar imagen")
            print("- Presiona ESPACIO para capturar imagen")
            print("=====================================")
            
            # Cola para recibir frames
            video_queue = device.getOutputQueue("video", maxSize=4, blocking=False)
            
            capture_count = 0
            
            while True:
                # Obtener frame
                in_video = video_queue.get()
                
                if in_video is not None:
                    # Convertir a OpenCV format
                    frame = in_video.getCvFrame()
                    
                    # Agregar información en la imagen
                    cv2.putText(frame, "OAK-4D R9 - Serial: 2533390442", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(frame, "IP: 192.168.200.126", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, f"Capturas realizadas: {capture_count}", (10, 110), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Mostrar resolución
                    height, width = frame.shape[:2]
                    cv2.putText(frame, f"Resolucion: {width}x{height}", (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Instrucciones
                    cv2.putText(frame, "Presiona 'q'=salir, 's'/'ESPACIO'=capturar", 
                               (10, frame.shape[0] - 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Mostrar imagen
                    cv2.imshow("OAK-4D R9 Camera Live Feed", frame)
                    
                    # Procesar teclas
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord('q'):
                        print("👋 Saliendo...")
                        break
                    elif key == ord('s') or key == ord(' '):  # 's' o espacio
                        # Capturar imagen
                        import time
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"captura_oak4d_{timestamp}.jpg"
                        
                        # Guardar con alta calidad
                        cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        capture_count += 1
                        print(f"📸 Imagen {capture_count} guardada: {filename}")
    
    except Exception as e:
        print(f"❌ Error al conectar con la cámara: {e}")
        print("\nPosibles soluciones:")
        print("1. Verifica que la cámara OAK-4D esté encendida")
        print("2. Verifica la conexión de red")
        print("3. Reinicia la cámara")
        print("4. Verifica que no haya firewall bloqueando")
    
    finally:
        cv2.destroyAllWindows()
        print("✅ Programa finalizado")

if __name__ == "__main__":
    print("=== Programa de Captura OAK-4D R9 ===")
    print("Versión optimizada para DepthAI 3.0+")
    print("Cámara: Luxonis KalamaP OAK4-D R9")
    print("Serial: 2533390442")
    print("IP: 192.168.200.126")
    print("=" * 45)
    
    capture_image()