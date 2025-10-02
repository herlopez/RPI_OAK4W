#!/usr/bin/env python3

"""
Programa avanzado para vista previa en tiempo real de la cámara OAK-4W
Este script muestra una vista previa continua con información adicional.
"""

import cv2
import depthai as dai
import numpy as np
import time

def preview_camera():
    """
    Muestra vista previa en tiempo real de la cámara OAK-4W con información adicional
    """
    # Crear pipeline de DepthAI
    pipeline = dai.Pipeline()
    
    # Definir fuente y salida de color
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    xout_rgb = pipeline.create(dai.node.XLinkOut)
    
    xout_rgb.setStreamName("rgb")
    
    # Configurar cámara RGB con mayor resolución
    cam_rgb.setPreviewSize(1280, 720)  # 720p
    cam_rgb.setInterleaved(False)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
    cam_rgb.setFps(30)  # 30 FPS
    
    # Conectar la cámara a la salida
    cam_rgb.preview.link(xout_rgb.input)
    
    # Variables para FPS
    fps_counter = 0
    start_time = time.time()
    fps = 0
    
    # Conectar al dispositivo y empezar pipeline
    try:
        with dai.Device(pipeline) as device:
            print("Conectado a la cámara OAK-4W")
            print(f"Dispositivo: {device.getDeviceName()}")
            print("Vista previa iniciada - Presiona 'q' para salir, 's' para capturar")
            
            # Cola de salida para frames RGB
            q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            
            while True:
                in_rgb = q_rgb.get()
                
                if in_rgb is not None:
                    # Convertir a OpenCV frame
                    frame = in_rgb.getCvFrame()
                    
                    # Convertir de RGB a BGR para OpenCV
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # Calcular FPS
                    fps_counter += 1
                    if fps_counter % 30 == 0:  # Actualizar cada 30 frames
                        end_time = time.time()
                        fps = 30 / (end_time - start_time)
                        start_time = time.time()
                    
                    # Agregar información de texto en la imagen
                    cv2.putText(frame_bgr, f"FPS: {fps:.1f}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame_bgr, f"Resolucion: {frame.shape[1]}x{frame.shape[0]}", 
                               (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame_bgr, "Presiona 'q' para salir, 's' para capturar", 
                               (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Mostrar la imagen
                    cv2.imshow("OAK-4W Vista Previa", frame_bgr)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        # Capturar imagen
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"captura_{timestamp}.jpg"
                        cv2.imwrite(filename, frame_bgr)
                        print(f"Imagen guardada como: {filename}")
    
    except RuntimeError as e:
        print(f"Error al conectar con la cámara: {e}")
        print("Posibles soluciones:")
        print("1. Verifica que la cámara OAK-4W esté conectada vía USB")
        print("2. Asegúrate de que no haya otro programa usando la cámara")
        print("3. Reinicia la conexión USB")
        return None
    
    finally:
        cv2.destroyAllWindows()
        print("Vista previa finalizada")

if __name__ == "__main__":
    print("=== Vista previa OAK-4W ===")
    print("Este programa muestra una vista previa en tiempo real")
    print("Controles:")
    print("- 'q': Salir")
    print("- 's': Capturar imagen")
    print("=" * 40)
    
    preview_camera()