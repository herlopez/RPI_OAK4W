#!/usr/bin/env python3

"""
Programa para capturar y guardar imágenes de la cámara OAK-4W
Este script permite capturar imágenes individuales y guardarlas con diferentes opciones.
"""

import cv2
import depthai as dai
import numpy as np
import time
import os
from datetime import datetime

def capture_and_save():
    """
    Captura y guarda imágenes desde la cámara OAK-4W
    """
    # Crear directorio de salida si no existe
    output_dir = "capturas"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Directorio '{output_dir}' creado")
    
    # Crear pipeline de DepthAI
    pipeline = dai.Pipeline()
    
    # Definir fuente y salida de color
    cam_rgb = pipeline.create(dai.node.ColorCamera)
    xout_rgb = pipeline.create(dai.node.XLinkOut)
    
    xout_rgb.setStreamName("rgb")
    
    # Configurar cámara RGB para máxima calidad
    cam_rgb.setPreviewSize(1920, 1080)  # Full HD
    cam_rgb.setInterleaved(False)
    cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
    cam_rgb.setFps(15)  # Menor FPS para mejor calidad
    
    # Conectar la cámara a la salida
    cam_rgb.preview.link(xout_rgb.input)
    
    capture_count = 0
    
    try:
        with dai.Device(pipeline) as device:
            print("Conectado a la cámara OAK-4W")
            print(f"Dispositivo: {device.getDeviceName()}")
            print("\nModo de captura iniciado")
            print("Controles:")
            print("- ESPACIO: Capturar imagen")
            print("- 'c': Capturar múltiples (cada 2 segundos)")
            print("- 'q': Salir")
            print("- 's': Capturar serie de 5 imágenes")
            print("=" * 50)
            
            # Cola de salida para frames RGB
            q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            
            continuous_mode = False
            series_mode = False
            series_count = 0
            last_capture_time = time.time()
            
            while True:
                in_rgb = q_rgb.get()
                
                if in_rgb is not None:
                    # Convertir a OpenCV frame
                    frame = in_rgb.getCvFrame()
                    
                    # Convertir de RGB a BGR para OpenCV
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # Agregar información de estado
                    status_text = "LISTO PARA CAPTURAR"
                    if continuous_mode:
                        status_text = "MODO CONTINUO ACTIVO"
                    elif series_mode:
                        status_text = f"SERIE: {series_count}/5"
                    
                    cv2.putText(frame_bgr, status_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame_bgr, f"Capturas: {capture_count}", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(frame_bgr, f"Res: {frame.shape[1]}x{frame.shape[0]}", 
                               (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Mostrar vista previa (redimensionada para pantalla)
                    preview = cv2.resize(frame_bgr, (960, 540))  # 50% del tamaño original
                    cv2.imshow("OAK-4W Captura de Imágenes", preview)
                    
                    key = cv2.waitKey(1) & 0xFF
                    current_time = time.time()
                    
                    # Capturar imagen individual
                    if key == ord(' '):  # Espacio
                        capture_count += 1
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                        filename = os.path.join(output_dir, f"imagen_{timestamp}.jpg")
                        
                        # Guardar imagen a resolución completa
                        cv2.imwrite(filename, frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        print(f"✓ Imagen {capture_count} guardada: {filename}")
                    
                    # Modo continuo
                    elif key == ord('c'):
                        continuous_mode = not continuous_mode
                        print(f"Modo continuo: {'ACTIVADO' if continuous_mode else 'DESACTIVADO'}")
                    
                    # Serie de imágenes
                    elif key == ord('s'):
                        if not series_mode:
                            series_mode = True
                            series_count = 0
                            print("Iniciando serie de 5 imágenes...")
                    
                    # Salir
                    elif key == ord('q'):
                        break
                    
                    # Captura automática en modo continuo
                    if continuous_mode and current_time - last_capture_time >= 2.0:
                        capture_count += 1
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                        filename = os.path.join(output_dir, f"continua_{timestamp}.jpg")
                        
                        cv2.imwrite(filename, frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        print(f"📸 Captura automática {capture_count}: {filename}")
                        last_capture_time = current_time
                    
                    # Serie de imágenes
                    if series_mode and current_time - last_capture_time >= 1.0:
                        series_count += 1
                        capture_count += 1
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                        filename = os.path.join(output_dir, f"serie_{series_count}_{timestamp}.jpg")
                        
                        cv2.imwrite(filename, frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        print(f"📷 Serie {series_count}/5: {filename}")
                        last_capture_time = current_time
                        
                        if series_count >= 5:
                            series_mode = False
                            print("✓ Serie completada!")
    
    except RuntimeError as e:
        print(f"❌ Error al conectar con la cámara: {e}")
        print("\nSoluciones sugeridas:")
        print("1. Verifica la conexión USB de la cámara OAK-4W")
        print("2. Cierra otras aplicaciones que puedan usar la cámara")
        print("3. Reinicia el dispositivo USB")
        print("4. Verifica que las librerías estén instaladas correctamente")
        return None
    
    finally:
        cv2.destroyAllWindows()
        print(f"\n✓ Sesión finalizada. Total de imágenes capturadas: {capture_count}")
        if capture_count > 0:
            print(f"📁 Imágenes guardadas en: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    print("=== Capturador de Imágenes OAK-4W ===")
    print("Este programa permite capturar imágenes de alta calidad")
    print("Resolución: 1920x1080 (Full HD)")
    print("Calidad JPEG: 95%")
    print("=" * 50)
    
    capture_and_save()