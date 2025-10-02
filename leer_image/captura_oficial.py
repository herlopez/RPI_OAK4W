#!/usr/bin/env python3

"""
Programa OFICIAL para capturar imágenes de la cámara OAK-4D R9
Basado en el ejemplo oficial de DepthAI V3: "Display all cameras"
Documentación: https://docs.luxonis.com/software-v3/depthai/examples/camera/camera_all/

Cámara detectada: Luxonis KalamaP OAK4-D R9 (Serial: 2533390442)
IP: 192.168.200.126
"""

import cv2
import depthai as dai
import time

def main():
    """
    Función principal usando la API oficial de DepthAI V3
    """
    print("🚀 Iniciando captura con API oficial DepthAI V3...")
    
    try:
        # Crear dispositivo y pipeline (API oficial V3)
        device = dai.Device()
        
        print(f"✓ Dispositivo conectado: {device.getDeviceName()}")
        print(f"✓ Cámaras disponibles: {device.getConnectedCameras()}")
        
        with dai.Pipeline(device) as pipeline:
            outputQueues = {}
            sockets = device.getConnectedCameras()
            
            print(f"📸 Configurando {len(sockets)} cámaras...")
            
            # Crear nodos de cámara para cada socket disponible
            for socket in sockets:
                print(f"  - Configurando cámara en socket: {socket}")
                cam = pipeline.create(dai.node.Camera).build(socket)
                outputQueues[str(socket)] = cam.requestFullResolutionOutput().createOutputQueue()
            
            print("\n🎥 ¡CAPTURA INICIADA!")
            print("=" * 50)
            print("📋 CONTROLES:")
            print("  • 'q' o 'Q': Salir del programa")
            print("  • 's' o 'S': Capturar y guardar todas las cámaras")
            print("  • ESPACIO: Capturar y guardar todas las cámaras")
            print("=" * 50)
            
            # Iniciar pipeline
            pipeline.start()
            
            capture_count = 0
            
            # Bucle principal de captura
            while pipeline.isRunning():
                frames = {}
                
                # Obtener frames de todas las cámaras
                for name in outputQueues.keys():
                    queue = outputQueues[name]
                    if queue.has():
                        videoIn = queue.get()
                        assert isinstance(videoIn, dai.ImgFrame)
                        
                        # Obtener frame OpenCV
                        frame = videoIn.getCvFrame()
                        frames[name] = frame
                        
                        # Agregar información overlay
                        info_frame = frame.copy()
                        
                        # Información del dispositivo
                        cv2.putText(info_frame, f"OAK-4D R9 - Socket: {name}", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(info_frame, f"Serial: 2533390442", (10, 70), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(info_frame, f"IP: 192.168.200.126", (10, 110), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        # Información técnica
                        height, width = frame.shape[:2]
                        cv2.putText(info_frame, f"Resolucion: {width}x{height}", (10, 150), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(info_frame, f"Capturas: {capture_count}", (10, 190), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        
                        # Timestamp
                        timestamp = time.strftime("%H:%M:%S")
                        cv2.putText(info_frame, f"Tiempo: {timestamp}", (10, 230), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        
                        # Controles en la parte inferior
                        cv2.putText(info_frame, "Q=salir | S/ESPACIO=capturar", 
                                   (10, info_frame.shape[0] - 20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        
                        # Mostrar frame con información
                        cv2.imshow(f"OAK-4D R9 - Camara {name}", info_frame)
                
                # Procesar input del teclado
                key = cv2.waitKey(1) & 0xFF
                
                # Salir con 'q' o 'Q'
                if key == ord('q') or key == ord('Q'):
                    print("👋 Cerrando aplicación...")
                    break
                
                # Capturar con 's', 'S' o ESPACIO
                elif key == ord('s') or key == ord('S') or key == ord(' '):
                    if frames:
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        capture_count += 1
                        
                        print(f"\n📸 Capturando imágenes #{capture_count}...")
                        
                        for socket_name, frame in frames.items():
                            filename = f"captura_oak4d_{socket_name}_{timestamp}.jpg"
                            success = cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                            
                            if success:
                                height, width = frame.shape[:2]
                                print(f"  ✓ {filename} - {width}x{height}")
                            else:
                                print(f"  ❌ Error guardando {filename}")
                        
                        print(f"📁 Total capturado: {len(frames)} imágenes")
        
        print(f"\n✅ Sesión finalizada exitosamente")
        print(f"📊 Total de capturas realizadas: {capture_count}")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        print(f"Tipo de error: {type(e).__name__}")
        
        # Información de depuración
        print("\n🔧 Información de depuración:")
        try:
            devices = dai.Device.getAllAvailableDevices()
            print(f"Dispositivos disponibles: {len(devices)}")
            for device in devices:
                print(f"  - {device}")
        except Exception as debug_error:
            print(f"Error obteniendo dispositivos: {debug_error}")
        
        return False
    
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("=" * 60)
    print("    CAPTURADOR OFICIAL OAK-4D R9 - DepthAI V3")
    print("=" * 60)
    print("🎯 Basado en ejemplo oficial de Luxonis")
    print("📖 Documentación: docs.luxonis.com/software-v3/")
    print("🔗 Código fuente: github.com/luxonis/depthai-core")
    print()
    print("📋 Información del dispositivo:")
    print("  • Modelo: Luxonis KalamaP OAK4-D R9")
    print("  • Serial: 2533390442")
    print("  • IP: 192.168.200.126")
    print(f"  • DepthAI: v{dai.__version__}")
    print("=" * 60)
    
    # Ejecutar programa principal
    success = main()
    
    if success:
        print("\n🎉 ¡Programa ejecutado exitosamente!")
        print("📝 Las imágenes capturadas se guardaron en el directorio actual")
    else:
        print("\n❌ El programa terminó con errores")
        print("💡 Verifica la conexión de red y que la cámara esté encendida")
        
    print("\n¡Gracias por usar el capturador oficial OAK-4D R9! 👋")