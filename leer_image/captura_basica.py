#!/usr/bin/env python3

"""
Programa básico para leer una imagen de la cámara OAK-4D R9
Este script captura imágenes de la cámara OAK-4D conectada por red.
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
    # Crear pipeline de DepthAI
    pipeline = dai.Pipeline()
    
    # Definir fuente y salida de color (API 3.0+)
    cam_rgb = pipeline.create(dai.node.Camera)
    
    # Configurar cámara RGB para OAK-4D
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)  # Cámara principal
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
    cam_rgb.setFps(30)
    
    # Crear salida para el stream de video
    video_out = pipeline.create(dai.node.VideoEncoder)
    video_out.setDefaultProfilePreset(cam_rgb.getFps(), dai.VideoEncoderProperties.Profile.MJPEG)
    
    # Configurar salida XLink
    xout = pipeline.create(dai.node.XLinkOut)
    xout.setStreamName("video")
    
    # Conectar nodos
    cam_rgb.video.link(video_out.input)
    video_out.bitstream.link(xout.input)
    
    # Buscar dispositivo específico por número de serie
    device_info = None
    found_devices = dai.Device.getAllAvailableDevices()
    
    print("Buscando cámara OAK-4D R9...")
    for device in found_devices:
        print(f"Dispositivo encontrado: {device.getMxId()} - {device.desc.name}")
        if "2533390442" in device.getMxId():
            device_info = device
            print(f"✓ Cámara OAK-4D R9 encontrada: {device.getMxId()}")
            break
    
    # Conectar al dispositivo y empezar pipeline
    try:
        # Si encontramos el dispositivo específico, usarlo; sino, usar el primero disponible
        if device_info:
            with dai.Device(pipeline, device_info) as device:
                print(f"Conectado a la cámara OAK-4D R9 (Serial: {device.getMxId()})")
                _run_capture_loop(device)
        else:
            print("Dispositivo específico no encontrado, intentando con el primer dispositivo disponible...")
            with dai.Device(pipeline) as device:
                print(f"Conectado a dispositivo: {device.getMxId()}")
                _run_capture_loop(device)
    
    except RuntimeError as e:
        print(f"Error al conectar con la cámara: {e}")
        print("\nSoluciones sugeridas:")
        print("1. Verifica que la cámara OAK-4D esté encendida")
        print("2. Verifica la conexión de red (IP: 192.168.200.126)")
        print("3. Verifica que no haya firewall bloqueando la conexión")
        print("4. Asegúrate de estar en la misma red que la cámara")
        return None
    
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None
    
    finally:
        cv2.destroyAllWindows()

def _run_capture_loop(device):
    """
    Ejecuta el bucle principal de captura
    """
    # Cola de salida para frames de video
    q_video = device.getOutputQueue(name="video", maxSize=4, blocking=False)
    
    print("\n=== CÁMARA OAK-4D R9 ACTIVA ===")
    print("Mostrando vista previa...")
    print("Controles:")
    print("- Presiona 'q' para salir")
    print("- Presiona 's' para capturar imagen")
    print("=====================================")
    
    capture_count = 0
    
    while True:
        in_video = q_video.get()  # Obtener frame
        
        if in_video is not None:
            # Decodificar el frame MJPEG
            frame_data = in_video.getData()
            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            if frame is not None:
                # Agregar información en la imagen
                cv2.putText(frame, "OAK-4D R9 - Serial: 2533390442", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "IP: 192.168.200.126", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"Capturas: {capture_count}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, "Presiona 'q' para salir, 's' para capturar", 
                           (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Mostrar la imagen
                cv2.imshow("OAK-4D R9 Camera", frame)
                
                # Manejar teclas
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Capturar imagen
                    import time
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"captura_oak4d_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    capture_count += 1
                    print(f"✓ Imagen guardada: {filename}")
        else:
            # Pequeña pausa si no hay frame disponible
            cv2.waitKey(1)

if __name__ == "__main__":
    print("=== Programa de captura básica OAK-4D R9 ===")
    print("Cámara: Luxonis KalamaP OAK4-D R9")
    print("Serial: 2533390442")
    print("IP: 192.168.200.126")
    print("Este programa muestra la imagen en tiempo real de la cámara")
    print("Presiona 'q' para salir, 's' para capturar imagen\n")
    
    capture_image()