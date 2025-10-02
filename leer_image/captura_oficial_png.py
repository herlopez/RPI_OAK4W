#!/usr/bin/env python3
"""
Versión PNG del capturador oficial para OAK-4D R9 (DepthAI V3)
Basado en `captura_oficial.py` pero guardando imágenes en formato PNG.

Diferencias clave:
- Guarda archivos .png en lugar de .jpg
- Permite configurar nivel de compresión PNG (0 = sin compresión, 9 = máxima)
- Opción de prefijo de archivo configurable por variable de entorno PNG_PREFIX

Formato de archivo: captura_png_<SOCKET>_<YYYYmmdd_HHMMSS>_<WxH>.png
"""

import os
import cv2
import time
import depthai as dai
import argparse
from typing import Dict, List, Tuple
import statistics

def get_png_compression():
    """Obtiene el nivel de compresión PNG desde la variable de entorno PNG_COMPRESSION (0-9)."""
    try:
        val = int(os.environ.get("PNG_COMPRESSION", "3"))  # Valor por defecto razonable
        return max(0, min(9, val))
    except ValueError:
        return 3

def get_prefix():
    return os.environ.get("PNG_PREFIX", "captura_png")

def main(headless: bool = False,
         auto_interval: float | None = None,
         one_shot: bool = False,
         wait_all: bool = False,
         wait_timeout: float = 2.0,
         warmup_frames: int = 5,
         min_frames_each: int = 1,
         downscale: Tuple[int,int] | None = None,
         min_brightness: float | None = None,
         brightness_retry: int = 2,
         brightness_wait: float = 0.5,
         min_sharpness: float | None = None,
         sharpness_frames: int = 3,
         focus_scan: bool = False,
         focus_positions: List[int] | None = None,
         focus_only_cam: str | None = None):
    """Lógica principal de captura.

    Parámetros:
        headless: Si True, no abre ventanas ni usa cv2.imshow (modo servidor / sin GUI).
        auto_interval: Si se establece (segundos), captura automáticamente cada N segundos.
        one_shot: Si True, realiza una sola captura y termina (ignora auto_interval).
    """
    print("🚀 Iniciando capturador PNG DepthAI V3...")
    compression_level = get_png_compression()
    prefix = get_prefix()
    mode_txt = "HEADLESS" if headless else "GUI"
    print(f"🖥️  Modo: {mode_txt}")
    if auto_interval and not one_shot:
        print(f"⏱️  Captura automática cada {auto_interval:.2f}s")
    if one_shot:
        print("📷 Modo one-shot: se realizará una sola captura y se saldrá")
    if wait_all:
        print(f"🕒 Modo espera por TODAS las cámaras (timeout {wait_timeout:.1f}s)")
    print(f"⚙️  Compresión PNG: {compression_level} (0=rápido, 9=pequeño)")
    print(f"⚙️  Prefijo archivo: {prefix}")
    if warmup_frames > 0:
        print(f"🔥 Warmup descartando primeros {warmup_frames} frames por cámara")
    if downscale:
        print(f"🔽 Reducción solicitada (preview) a {downscale[0]}x{downscale[1]} (no afecta resolución nativa guardada)")
    if min_brightness is not None:
        print(f"🌗 Brillo mínimo requerido: {min_brightness:.1f} (promedio 0-255), reintentos={brightness_retry}")
    if min_sharpness is not None:
        print(f"🔎 Nitidez mínima (varianza Laplaciana) requerida: {min_sharpness:.1f} (promedio sobre {sharpness_frames} frames)")
    if focus_scan:
        if not focus_positions:
            focus_positions = [50, 80, 110, 140, 170, 200]
        print(f"🎯 Escaneo de foco habilitado. Posiciones: {focus_positions}")
        if focus_only_cam:
            print(f"➡️  Se enfocará solo cámara: {focus_only_cam}")

    try:
        device = dai.Device()
        print(f"✓ Dispositivo conectado: {device.getDeviceName()}")
        sockets = device.getConnectedCameras()
        print(f"✓ Cámaras detectadas: {sockets}")

        with dai.Pipeline(device) as pipeline:
            outputQueues = {}
            cam_nodes: Dict[str, any] = {}
            for socket in sockets:
                cam = pipeline.create(dai.node.Camera).build(socket)
                out = cam.requestFullResolutionOutput()
                outputQueues[str(socket)] = out.createOutputQueue()
                cam_nodes[str(socket)] = cam

            print("\n🎥 Captura iniciada (formato PNG)")
            if headless:
                print("Modo headless: no se mostrarán ventanas.")
                if not (auto_interval or one_shot):
                    print("⚠️  No se ha definido auto_interval ni one_shot; el programa no capturará nada.")
                    print("     Use --interval SEG o --one-shot, o establezca AUTO_CAPTURE_INTERVAL en entorno.")
            else:
                print("Controles: Q=salir | S/ESPACIO=capturar todas las cámaras")
            pipeline.start()

            capture_count = 0
            last_auto_capture = 0.0
            # Contadores de warmup por cámara
            warmup_counter = {str(s): 0 for s in sockets}
            per_cam_frames = {str(s): 0 for s in sockets}

            # Intento de escaneo de foco (solo antes del bucle principal)
            if focus_scan:
                # Solo si node soporta métodos de foco
                target_cams = [focus_only_cam] if focus_only_cam else list(cam_nodes.keys())
                for cam_name in target_cams:
                    cam_node = cam_nodes.get(cam_name)
                    if cam_node is None:
                        print(f"⚠️ Cámara {cam_name} no encontrada para focus scan")
                        continue
                    # Verificamos métodos
                    supported = any(hasattr(cam_node, attr) for attr in ["setManualFocus", "setFocus", "setLensPosition"])
                    if not supported:
                        print(f"⚠️ Cámara {cam_name} no expone API de enfoque manual (posible foco fijo)")
                        continue
                    print(f"🔄 Escaneo de foco en {cam_name} ...")
                    best_var = -1.0
                    best_pos = None
                    # Para obtener frames necesitamos iniciar pipeline primero, garantizado arriba
                    # Consumimos algunos frames iniciales para estabilizar
                    pre_queue = outputQueues.get(cam_name)
                    t0 = time.time()
                    while time.time() - t0 < 1.0 and pre_queue and pre_queue.has():
                        pre_queue.get()
                    scan_positions = focus_positions or []
                    for pos in scan_positions:
                        try:
                            if hasattr(cam_node, 'setManualFocus'):
                                cam_node.setManualFocus(pos)
                            elif hasattr(cam_node, 'setFocus'):
                                cam_node.setFocus(pos)
                            elif hasattr(cam_node, 'setLensPosition'):
                                cam_node.setLensPosition(pos)
                        except Exception as e:
                            print(f"  ⚠️ No se pudo fijar posición {pos}: {e}")
                            continue
                        time.sleep(0.15)  # pequeño delay para que se aplique
                        # tomar un frame para evaluar
                        sharp_var = None
                        eval_start = time.time()
                        while time.time() - eval_start < 0.5:
                            if pre_queue.has():
                                frame_eval = pre_queue.get().getCvFrame()
                                gray_eval = cv2.cvtColor(frame_eval, cv2.COLOR_BGR2GRAY) if len(frame_eval.shape)==3 else frame_eval
                                sharp_var = cv2.Laplacian(gray_eval, cv2.CV_64F).var()
                                break
                        if sharp_var is None:
                            continue
                        print(f"  Pos {pos}: nitidez={sharp_var:.1f}")
                        if sharp_var > best_var:
                            best_var = sharp_var
                            best_pos = pos
                    if best_pos is not None:
                        print(f"✅ Mejor foco {cam_name}: posición {best_pos} (nitidez {best_var:.1f})")
                        try:
                            if hasattr(cam_node, 'setManualFocus'):
                                cam_node.setManualFocus(best_pos)
                            elif hasattr(cam_node, 'setFocus'):
                                cam_node.setFocus(best_pos)
                            elif hasattr(cam_node, 'setLensPosition'):
                                cam_node.setLensPosition(best_pos)
                        except Exception:
                            pass
                    else:
                        print(f"⚠️ No se determinó mejor foco en {cam_name}")

            while pipeline.isRunning():
                frames: Dict[str, any] = {}

                start_wait_cycle = time.time()
                # Estrategia: si wait_all, iteramos hasta conseguir todos los sockets o timeout
                while True:
                    acquired_any = False
                    for name, queue in outputQueues.items():
                        if name not in frames and queue.has():
                            img_frame = queue.get()
                            frame = img_frame.getCvFrame()
                            # Warmup: descartar primeros N frames por cámara
                            if warmup_counter[name] < warmup_frames:
                                warmup_counter[name] += 1
                                continue
                            per_cam_frames[name] += 1
                            frames[name] = frame
                            acquired_any = True
                            if not headless:
                                overlay = frame.copy()
                                h, w = frame.shape[:2]
                                if downscale:
                                    try:
                                        overlay = cv2.resize(overlay, downscale, interpolation=cv2.INTER_LINEAR)
                                        h, w = overlay.shape[:2]
                                    except Exception:
                                        pass
                                cv2.putText(overlay, f"{name} {w}x{h}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                                cv2.putText(overlay, f"Capturas: {capture_count}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
                                missing = [s for s in outputQueues.keys() if s not in frames]
                                if wait_all and missing:
                                    cv2.putText(overlay, f"Esperando: {','.join(missing)}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,200,255), 1)
                                # Mostrar estado warmup
                                if warmup_counter[name] < warmup_frames:
                                    cv2.putText(overlay, f"WARMUP {warmup_counter[name]}/{warmup_frames}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,165,255), 1)
                                cv2.putText(overlay, "Q=Salir S/ESPACIO=Capturar", (10, overlay.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)
                                cv2.imshow(f"PNG - {name}", overlay)
                    if not wait_all:
                        break  # No necesitamos esperar a todos
                    else:
                        have_all = len(frames) == len(outputQueues)
                        timed_out = (time.time() - start_wait_cycle) >= wait_timeout
                        if have_all or timed_out:
                            if timed_out and not have_all and one_shot:
                                print(f"⚠️ Timeout esperando todas las cámaras. Se capturarán solo: {list(frames.keys())}")
                            break
                        # Pequeño respiro para no bloquear CPU
                        if not acquired_any:
                            time.sleep(0.005)
                        if not headless:
                            if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q')):
                                print("👋 Saliendo...")
                                return True

                do_capture = False
                # Modo headless con intervalo automático
                if headless and auto_interval and frames:
                    now = time.time()
                    if (now - last_auto_capture) >= auto_interval:
                        do_capture = True
                        last_auto_capture = now
                
                key = 255
                if not headless:
                    key = cv2.waitKey(1) & 0xFF
                else:
                    # Pequeño sleep para no consumir CPU al 100%
                    time.sleep(0.01)

                if not headless and key in (ord('q'), ord('Q')):
                    print("👋 Saliendo...")
                    break
                if not headless and key in (ord('s'), ord('S'), ord(' ')) and frames:
                    do_capture = True
                if one_shot and frames and capture_count == 0:
                    do_capture = True
                if do_capture and frames:
                    # Verificar que cada cámara tenga al menos min_frames_each frames (para asegurar exposición estable)
                    lacking = [cam for cam, cnt in per_cam_frames.items() if cnt < min_frames_each]
                    if lacking:
                        print(f"⏳ Aún no se cumplen min_frames_each para: {lacking} (se pospone captura)")
                        do_capture = False
                        continue

                    # Check brightness if needed
                    attempt = 0
                    captured_frames = frames
                    # --- BRIGHTNESS LOOP ---
                    while min_brightness is not None and attempt <= brightness_retry:
                        too_dark = []
                        for sock, frame in captured_frames.items():
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape)==3 else frame
                            mean_val = float(gray.mean())
                            if mean_val < min_brightness:
                                too_dark.append((sock, mean_val))
                        if not too_dark:
                            break
                        attempt += 1
                        if attempt > brightness_retry:
                            print(f"⚠️ Continúa oscuro después de {brightness_retry} reintentos: {too_dark}")
                            break
                        print(f"🌑 Frames oscuros {too_dark}, esperando {brightness_wait:.2f}s para nueva lectura (intento {attempt}/{brightness_retry})")
                        time.sleep(brightness_wait)
                        # Recolectar nuevos frames oscuros
                        for sock, queue in outputQueues.items():
                            if queue.has():
                                new_frame = queue.get().getCvFrame()
                                captured_frames[sock] = new_frame

                    # --- SHARPNESS CHECK ---
                    if min_sharpness is not None:
                        sharp_attempts = 0
                        while sharp_attempts < 3:  # evitar bucle infinito
                            sharp_values = []
                            for sock, frame in list(captured_frames.items())[:sharpness_frames]:
                                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape)==3 else frame
                                lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                                sharp_values.append(lap_var)
                            if sharp_values:
                                avg_sharp = sum(sharp_values) / len(sharp_values)
                                if avg_sharp < min_sharpness:
                                    print(f"🔁 Nitidez promedio {avg_sharp:.1f} < {min_sharpness:.1f}. Reintentando en 0.3s...")
                                    time.sleep(0.3)
                                    # refrescar frames disponibles
                                    for sock, queue in outputQueues.items():
                                        if queue.has():
                                            new_frame = queue.get().getCvFrame()
                                            captured_frames[sock] = new_frame
                                    sharp_attempts += 1
                                    continue
                                else:
                                    print(f"🔎 Nitidez OK ({avg_sharp:.1f})")
                                break
                            else:
                                break

                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    capture_count += 1
                    print(f"\n📸 Guardando lote #{capture_count} en PNG...")
                    for sock, frame in captured_frames.items():
                        h, w = frame.shape[:2]
                        filename = f"{prefix}_{sock}_{timestamp}_{w}x{h}.png"
                        success = cv2.imwrite(filename, frame, [cv2.IMWRITE_PNG_COMPRESSION, compression_level])
                        if success:
                            size_kb = os.path.getsize(filename) / 1024
                            if min_brightness is not None:
                                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape)==3 else frame
                                print(f"  ✓ {filename} ({size_kb:.1f} KB) brillo={gray.mean():.1f}")
                            else:
                                print(f"  ✓ {filename} ({size_kb:.1f} KB)")
                        else:
                            print(f"  ❌ Error guardando {filename}")
                    if one_shot:
                        print("✅ Captura única realizada. Saliendo...")
                        break

        print("\n✅ Sesión PNG finalizada.")
        print(f"Total lotes capturados: {capture_count}")
        return True
    except Exception as e:
        print(f"❌ Error en ejecución PNG: {e}")
        return False
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capturador PNG OAK-4D R9 (DepthAI V3)")
    parser.add_argument("--headless", action="store_true", help="Ejecuta sin ventanas y sin interacción.")
    parser.add_argument("--interval", type=float, default=None, help="Captura automática cada N segundos (headless).")
    parser.add_argument("--one-shot", action="store_true", help="Realiza una sola captura y termina.")
    parser.add_argument("--wait-all", action="store_true", help="Espera a tener frame de TODAS las cámaras antes de capturar (con timeout).")
    parser.add_argument("--wait-timeout", type=float, default=2.0, help="Tiempo máximo (s) esperando todas las cámaras (por defecto 2.0).")
    parser.add_argument("--warmup-frames", type=int, default=5, help="Frames iniciales a descartar por cámara (default 5).")
    parser.add_argument("--min-frames-each", type=int, default=1, help="Mínimo de frames válidos por cámara antes de permitir captura (default 1).")
    parser.add_argument("--downscale", type=str, default=None, help="Redimensionar SOLO la previsualización, formato WxH (ej 1280x720).")
    parser.add_argument("--min-brightness", type=float, default=None, help="Brillo medio mínimo (0-255); si menor reintenta.")
    parser.add_argument("--brightness-retry", type=int, default=2, help="Reintentos si oscuro (default 2).")
    parser.add_argument("--brightness-wait", type=float, default=0.5, help="Segundos entre reintentos de brillo (default 0.5).")
    parser.add_argument("--min-sharpness", type=float, default=None, help="Varianza Laplaciana mínima promedio para aceptar nitidez.")
    parser.add_argument("--sharpness-frames", type=int, default=3, help="Número de frames para promediar nitidez (default 3).")
    parser.add_argument("--focus-scan", action="store_true", help="Escanear varias posiciones de foco y elegir la mejor (si soportado).")
    parser.add_argument("--focus-positions", type=str, default=None, help="Lista de posiciones separadas por coma (ej 40,80,120,160).")
    parser.add_argument("--focus-only-cam", type=str, default=None, help="Aplicar escaneo de foco solo a un socket (ej CAM_A).")
    args = parser.parse_args()

    # Variables de entorno alternativas
    env_headless = os.environ.get("PNG_HEADLESS", "false").lower() in ("1", "true", "yes")
    headless = args.headless or env_headless
    env_interval = os.environ.get("AUTO_CAPTURE_INTERVAL")
    interval = args.interval
    if interval is None and env_interval:
        try:
            interval = float(env_interval)
        except ValueError:
            interval = None
    one_shot = args.one_shot or (os.environ.get("PNG_ONE_SHOT", "false").lower() in ("1","true","yes"))
    wait_all = args.wait_all or (os.environ.get("PNG_WAIT_ALL", "false").lower() in ("1","true","yes"))
    wait_timeout = args.wait_timeout
    env_timeout = os.environ.get("PNG_WAIT_TIMEOUT")
    if env_timeout:
        try:
            wait_timeout = float(env_timeout)
        except ValueError:
            pass

    print("="*70)
    print("  CAPTURADOR OAK-4D R9 - FORMATO PNG (DepthAI V3) - MODO EXTENDIDO")
    print("="*70)
    print(f"Versión DepthAI: {dai.__version__}")
    print("Variables de entorno soportadas:")
    print("  PNG_COMPRESSION (0-9)       | default=3")
    print("  PNG_PREFIX (prefijo)        | default='captura_png'")
    print("  PNG_HEADLESS (true/false)   | forzar modo sin GUI")
    print("  AUTO_CAPTURE_INTERVAL (seg) | intervalo automático")
    print("  PNG_ONE_SHOT (true/false)   | captura única")
    print("Ejemplos PowerShell:")
    print("  $env:PNG_HEADLESS=1; $env:AUTO_CAPTURE_INTERVAL=5; python captura_oficial_png.py")
    print("  python captura_oficial_png.py --headless --interval 10")
    print("  python captura_oficial_png.py --one-shot")
    print("="*70)
    downscale = None
    if args.downscale:
        try:
            parts = args.downscale.lower().split('x')
            downscale = (int(parts[0]), int(parts[1]))
        except Exception:
            print("⚠️ Formato inválido en --downscale, usar WxH, ejemplo 1280x720")
            downscale = None

    focus_positions = None
    if args.focus_positions:
        try:
            focus_positions = [int(x) for x in args.focus_positions.split(',') if x.strip().isdigit()]
        except Exception:
            print("⚠️ Formato inválido en --focus-positions, ignorando")

    main(headless=headless,
         auto_interval=interval,
         one_shot=one_shot,
         wait_all=wait_all,
         wait_timeout=wait_timeout,
         warmup_frames=args.warmup_frames,
         min_frames_each=args.min_frames_each,
         downscale=downscale,
         min_brightness=args.min_brightness,
         brightness_retry=args.brightness_retry,
         brightness_wait=args.brightness_wait,
         min_sharpness=args.min_sharpness,
         sharpness_frames=args.sharpness_frames,
         focus_scan=args.focus_scan,
         focus_positions=focus_positions,
         focus_only_cam=args.focus_only_cam)