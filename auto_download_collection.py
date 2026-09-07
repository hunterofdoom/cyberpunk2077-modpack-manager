import ctypes
import time
import os
import cv2
import numpy as np
from PIL import Image, ImageGrab

BASE_DIR = r"C:\Users\Audur\.gemini\antigravity-ide\brain\726a2fb3-76c5-4963-9697-3e9e178c5c9b\scratch"
TPL_VORTEX_PATH = os.path.join(BASE_DIR, "tpl_download_manually.png")
TPL_SLOW_PATH = os.path.join(BASE_DIR, "tpl_slow_download.png")
TPL_DONT_ASK_RGB_PATH = os.path.join(BASE_DIR, "tpl_btn_dont_ask_rgb.png")

user32 = ctypes.windll.user32

def attach_desktop():
    hdesk = user32.OpenDesktopW("default", 0, False, 0x01FF)
    if hdesk:
        user32.SetThreadDesktop(hdesk)

def click_coords(x, y):
    attach_desktop()
    nx = int(x * 65535 / 1920)
    ny = int(y * 65535 / 1080)
    user32.mouse_event(0x8001, nx, ny, 0, 0)
    time.sleep(0.04)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.04)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

def grab_screen():
    attach_desktop()
    im = ImageGrab.grab()
    return np.array(im)

def find_template(screen_img, tpl_img, threshold=0.88):
    res = cv2.matchTemplate(screen_img, tpl_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val >= threshold:
        h, w = tpl_img.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return True, center_x, center_y, max_val
    return False, 0, 0, max_val

def main():
    print("[*] Iniciando automatizador de colecciones de Vortex con soporte de Fallback...")
    tpl_vortex = cv2.imread(TPL_VORTEX_PATH, cv2.IMREAD_COLOR)
    tpl_slow = cv2.imread(TPL_SLOW_PATH, cv2.IMREAD_COLOR)
    tpl_dont_ask = cv2.imread(TPL_DONT_ASK_RGB_PATH, cv2.IMREAD_COLOR)

    idle_count = 0
    mods_downloaded = 29

    while True:
        try:
            screen_bgr = cv2.cvtColor(grab_screen(), cv2.COLOR_RGB2BGR)

            # 1. Comprobar si salta el Fallback Installer de Vortex (boton naranja)
            found_fallback, fx, fy, f_val = find_template(screen_bgr, tpl_dont_ask, threshold=0.92)
            if found_fallback:
                print(f"[!] Fallback Installer detectado ({f_val:.2f}). Clic en 'Yes, Install And Don't Ask Again' ({fx}, {fy})...")
                click_coords(fx, fy)
                idle_count = 0
                time.sleep(3.0)
                continue

            # 2. Comprobar si esta visible 'Download manually' en Vortex
            found_vortex, vx, vy, v_val = find_template(screen_bgr, tpl_vortex, threshold=0.92)
            if found_vortex:
                print(f"[+] 'Download manually' detectado en ({vx}, {vy}) con match {v_val:.2f}. Haciendo clic...")
                click_coords(vx, vy)
                idle_count = 0
                time.sleep(2.5) # Esperar a que abra la pestana del navegador
                continue

            # 3. Comprobar si esta visible 'Slow download' en la web de NexusMods
            found_slow, sx, sy, s_val = find_template(screen_bgr, tpl_slow, threshold=0.92)
            if found_slow:
                print(f"[+] 'Slow download' detectado en ({sx}, {sy}) con match {s_val:.2f}. Haciendo clic...")
                click_coords(sx, sy)
                mods_downloaded += 1
                idle_count = 0
                print(f"[v] Mod #{mods_downloaded} descargado. Esperando proxima solicitud...")
                time.sleep(5.5) # Esperar el conteo regresivo de NexusMods
                continue

            time.sleep(1.0)
            idle_count += 1
            if idle_count % 30 == 0:
                print(f"[*] Esperando siguiente ventana... ({idle_count}s sin cambios. Total descargados: {mods_downloaded})")

        except KeyboardInterrupt:
            print("\n[!] Automatizacion detenida por el usuario.")
            break
        except Exception as e:
            print(f"[!] Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
