#!/usr/bin/env python3

"""
Programa básico para capturar imágenes de la cámara OAK-4D R9
Versión FUNCIONAL para DepthAI 3.0+
Cámara detectada: Luxonis KalamaP OAK4-D R9 (Serial: 2533390442)
IP: 192.168.200.126
"""

import cv2
import depthai as dai
import numpy as np

def main():
    """
    Función principal de captura
    """
    print("🚀 Iniciando programa de captura OAK-4D R9...")
    
    # Verificar dispositivos disponibles
    devices = dai.Device.getAllAvailableDevices()
    if len(devices) == 0:
        print("❌ No se encontraron dispositivos OAK")
        return False
    
    print(f"✓ Dispositivo encontrado: {devices[0]}")
    
    # Crear pipeline
    pipeline = dai.Pipeline()
    
    # Configurar cámara RGB
    try:
        cam_rgb = pipeline.create(dai.node.ColorCamera)
        cam_rgb.setPreviewSize(640, 480)
        cam_rgb.setInterleaved(False)
        cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        
        # Crear salida para preview
        xout_rgb = pipeline.create(dai.node.XLinkOut)
        xout_rgb.setStreamName("rgb")
        
        # Conectar cámara a salida
        cam_rgb.preview.link(xout_rgb.input)
        
        print("✓ Pipeline configurado correctamente")
        
    except Exception as e:
        print(f"❌ Error configurando pipeline: {e}")
        return False
    
    # Conectar al dispositivo y ejecutar
    try:
        # Usar el dispositivo específico si está disponible
        device_info = devices[0]
        
        with dai.Device(pipeline, device_info) as device:
            print("🎥 ¡CONECTADO A OAK-4D R9!")
            print("=" * 40)
            print("Controles de captura:")
            print("- 'q' o 'Q': Salir del programa")
            print("- 's' o 'S': Capturar y guardar imagen")
            print("- ESPACIO: Capturar y guardar imagen")
            print("=" * 40)
            
            # Obtener cola de salida RGB
            q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            
            capture_count = 0
            
            while True:
                # Obtener frame RGB
                in_rgb = q_rgb.get()
                
                if in_rgb is not None:
                    # Convertir a formato OpenCV
                    frame = in_rgb.getCvFrame()
                    
                    # Información de overlay
                    cv2.putText(frame, "OAK-4D R9 CONECTADO", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(frame, f"Serial: 2533390442", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, f"IP: 192.168.200.126", (10, 110), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, f"Capturas realizadas: {capture_count}", (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Información técnica
                    height, width = frame.shape[:2]
                    cv2.putText(frame, f"Resolucion: {width}x{height}", (10, 190), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Instrucciones en la parte inferior
                    cv2.putText(frame, "Controles: Q=salir | S/ESPACIO=capturar", 
                               (10, frame.shape[0] - 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    
                    # Mostrar frame
                    cv2.imshow("OAK-4D R9 - Captura en Vivo", frame)
                    
                    # Procesar input del teclado
                    key = cv2.waitKey(1) & 0xFF
                    
                    # Salir con 'q' o 'Q'
                    if key == ord('q') or key == ord('Q'):
                        print("👋 Saliendo del programa...")
                        break
                    
                    # Capturar con 's', 'S' o ESPACIO
                    elif key == ord('s') or key == ord('S') or key == ord(' '):
                        import time
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        filename = f"captura_oak4d_{timestamp}.jpg"
                        
                        # Guardar imagen con alta calidad
                        success = cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        
                        if success:
                            capture_count += 1
                            print(f"📸 ¡Imagen {capture_count} guardada exitosamente!")
                            print(f"   📁 Archivo: {filename}")
                            print(f"   📏 Resolución: {width}x{height}")
                        else:
                            print("❌ Error al guardar la imagen")
        
        print(f"\n✅ Sesión finalizada")
        print(f"📊 Total de imágenes capturadas: {capture_count}")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la captura: {e}")
        print(f"Tipo de error: {type(e).__name__}")
        return False
    
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("=" * 50)
    print("    PROGRAMA DE CAPTURA OAK-4D R9")
    print("=" * 50)
    print("Cámara: Luxonis KalamaP OAK4-D R9")
    print("Serial: 2533390442")
    print("IP: 192.168.200.126")
    print(f"DepthAI: v{dai.__version__}")
    print("=" * 50)
    
    # Ejecutar programa principal
    success = main()
    
    if success:
        print("\n🎉 ¡Programa ejecutado exitosamente!")
    else:
        print("\n❌ El programa terminó con errores")
        
    print("\n¡Gracias por usar el capturador OAK-4D R9! 👋")