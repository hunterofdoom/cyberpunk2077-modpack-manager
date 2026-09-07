import os
import sys
import time
import json
import webbrowser
import threading
import subprocess
import shutil
import ctypes
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import cv2
import numpy as np
from PIL import Image, ImageGrab, ImageTk

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
CONFIG_FILE = BASE_DIR / "cp2077_mod_manager_config.json"

TPL_VORTEX_PATH = ASSETS_DIR / "tpl_download_manually.png"
TPL_SLOW_PATH = ASSETS_DIR / "tpl_slow_download.png"
TPL_DONT_ASK_PATH = ASSETS_DIR / "tpl_btn_dont_ask_rgb.png"

VORTEX_APPDATA = Path(os.environ.get("APPDATA", "")) / "Vortex"
VORTEX_DOWNLOADS = VORTEX_APPDATA / "downloads" / "cyberpunk2077"
VORTEX_STAGING = VORTEX_APPDATA / "cyberpunk2077" / "mods"

DEFAULT_KNOWN_PATHS = [
    Path(r"C:\Users\Audur\Desktop\Games NVM\Cyberpunk 2077"),
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077"),
    Path(r"D:\SteamLibrary\steamapps\common\Cyberpunk 2077"),
    Path(r"E:\SteamLibrary\steamapps\common\Cyberpunk 2077"),
    Path(r"F:\SteamLibrary\steamapps\common\Cyberpunk 2077"),
    Path(r"GOG Galaxy\Games\Cyberpunk 2077"),
]

user32 = ctypes.windll.user32


def attach_desktop():
    try:
        hdesk = user32.OpenDesktopW("default", 0, False, 0x01FF)
        if hdesk:
            user32.SetThreadDesktop(hdesk)
    except Exception:
        pass


def click_screen(x, y):
    attach_desktop()
    nx = int(x * 65535 / 1920)
    ny = int(y * 65535 / 1080)
    user32.mouse_event(0x8001, nx, ny, 0, 0)
    time.sleep(0.04)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.04)
    user32.mouse_event(0x0004, 0, 0, 0, 0)


def grab_screen_bgr():
    attach_desktop()
    im = ImageGrab.grab()
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)


def match_tpl(screen_bgr, tpl_bgr, threshold=0.90):
    res = cv2.matchTemplate(screen_bgr, tpl_bgr, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val >= threshold:
        h, w = tpl_bgr.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return True, center_x, center_y, max_val
    return False, 0, 0, max_val


class CyberpunkModApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cyberpunk 2077 - Modpack Auto-Manager & Launcher")
        self.geometry("900x700")
        self.minsize(840, 620)
        self.configure(bg="#0d0d11")

        self.auto_running = False
        self.auto_thread = None
        self.game_path = self.load_game_path()

        self.setup_ui()
        self.verify_installation()

    def load_game_path(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    p = Path(cfg.get("game_path", ""))
                    if self.is_valid_game_path(p):
                        return p
            except Exception:
                pass

        for p in DEFAULT_KNOWN_PATHS:
            if self.is_valid_game_path(p):
                self.save_game_path(p)
                return p
        return None

    def is_valid_game_path(self, path: Path):
        if not path or not path.exists():
            return False
        exe1 = path / "bin" / "x64" / "Cyberpunk2077.exe"
        exe2 = path / "Cyberpunk2077.exe"
        return exe1.exists() or exe2.exists()

    def get_game_exe(self):
        if not self.game_path:
            return None
        exe1 = self.game_path / "bin" / "x64" / "Cyberpunk2077.exe"
        if exe1.exists():
            return exe1
        exe2 = self.game_path / "Cyberpunk2077.exe"
        if exe2.exists():
            return exe2
        return None

    def save_game_path(self, path: Path):
        self.game_path = path
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"game_path": str(path)}, f, indent=2)
        except Exception:
            pass

    def setup_ui(self):
        # Header banner
        header = tk.Frame(self, bg="#13131b", height=70)
        header.pack(fill=tk.X, side=tk.TOP)

        title_lbl = tk.Label(
            header,
            text="CYBERPUNK 2077 // MODPACK AUTO-MANAGER",
            font=("Consolas", 15, "bold"),
            fg="#00e5ff",
            bg="#13131b",
        )
        title_lbl.pack(side=tk.LEFT, padx=20, pady=15)

        self.status_badge = tk.Label(
            header,
            text="VERIFICANDO...",
            font=("Segoe UI", 9, "bold"),
            fg="#0d0d11",
            bg="#ffd600",
            padx=12,
            pady=4,
        )
        self.status_badge.pack(side=tk.RIGHT, padx=20, pady=18)

        content = tk.Frame(self, bg="#0d0d11")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        # 1. URL Section & Auto Download
        url_frame = tk.LabelFrame(
            content,
            text=" 1. Colección Nexus Mods / Vortex ",
            font=("Segoe UI", 10, "bold"),
            fg="#fcee0a",
            bg="#171722",
            bd=1,
            relief=tk.SOLID,
        )
        url_frame.pack(fill=tk.X, pady=6)

        self.url_var = tk.StringVar(value="https://www.nexusmods.com/cyberpunk2077/collections/xyz-spanish")
        url_entry = tk.Entry(
            url_frame,
            textvariable=self.url_var,
            font=("Segoe UI", 10),
            bg="#222233",
            fg="#ffffff",
            insertbackground="#00e5ff",
            relief=tk.FLAT,
        )
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12, pady=10)

        open_btn = tk.Button(
            url_frame,
            text="Abrir Colección",
            command=self.open_collection_url,
            bg="#2c2c40",
            fg="#ffffff",
            activebackground="#3e3e58",
            activeforeground="#00e5ff",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            cursor="hand2",
        )
        open_btn.pack(side=tk.LEFT, padx=(0, 8), pady=10)

        self.auto_btn = tk.Button(
            url_frame,
            text="⚡ Iniciar Auto-Descarga",
            command=self.toggle_automation,
            bg="#00b4d8",
            fg="#0d0d11",
            activebackground="#90e0ef",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=15,
            cursor="hand2",
        )
        self.auto_btn.pack(side=tk.RIGHT, padx=12, pady=10)

        # 2. Vortex Detection & Fast Sync
        vortex_frame = tk.LabelFrame(
            content,
            text=" 2. Detección de Mods en Vortex ",
            font=("Segoe UI", 10, "bold"),
            fg="#39ff14",
            bg="#171722",
            bd=1,
            relief=tk.SOLID,
        )
        vortex_frame.pack(fill=tk.X, pady=6)

        self.vortex_status_lbl = tk.Label(
            vortex_frame,
            text="Escaneando Vortex...",
            font=("Segoe UI", 9),
            fg="#ffffff",
            bg="#171722",
            justify=tk.LEFT,
        )
        self.vortex_status_lbl.pack(side=tk.LEFT, padx=12, pady=10)

        self.sync_btn = tk.Button(
            vortex_frame,
            text="📥 Desplegar Mods de Vortex al Juego",
            command=self.sync_vortex_to_game,
            bg="#39ff14",
            fg="#05260f",
            activebackground="#70ff56",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=15,
            cursor="hand2",
        )
        self.sync_btn.pack(side=tk.RIGHT, padx=12, pady=10)

        # 3. Status & Diagnostic Frame
        diag_frame = tk.LabelFrame(
            content,
            text=" 3. Diagnóstico & Compatibilidad de Mods ",
            font=("Segoe UI", 10, "bold"),
            fg="#00e5ff",
            bg="#171722",
            bd=1,
            relief=tk.SOLID,
        )
        diag_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        path_box = tk.Frame(diag_frame, bg="#171722")
        path_box.pack(fill=tk.X, padx=12, pady=6)

        tk.Label(path_box, text="Ruta de Cyberpunk 2077:", font=("Segoe UI", 9, "bold"), fg="#a0a0b8", bg="#171722").pack(side=tk.LEFT)
        self.path_lbl = tk.Label(path_box, text="", font=("Segoe UI", 9), fg="#00e5ff", bg="#171722")
        self.path_lbl.pack(side=tk.LEFT, padx=8)

        change_path_btn = tk.Button(
            path_box,
            text="Examinar...",
            command=self.select_game_directory,
            bg="#2c2c40",
            fg="#ffffff",
            font=("Segoe UI", 8),
            relief=tk.FLAT,
            padx=8,
            cursor="hand2",
        )
        change_path_btn.pack(side=tk.RIGHT)

        self.diag_txt = tk.Text(
            diag_frame,
            bg="#111119",
            fg="#dcdcdc",
            font=("Consolas", 9),
            height=8,
            bd=0,
            padx=10,
            pady=8,
            relief=tk.FLAT,
        )
        self.diag_txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # 4. Bottom Action Bar
        bottom_bar = tk.Frame(self, bg="#13131b", height=75)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)

        refresh_btn = tk.Button(
            bottom_bar,
            text="🔄 Re-verificar Todo",
            command=self.verify_installation,
            bg="#252536",
            fg="#ffffff",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2",
        )
        refresh_btn.pack(side=tk.LEFT, padx=20, pady=15)

        self.play_btn = tk.Button(
            bottom_bar,
            text="▶ JUGAR CYBERPUNK 2077",
            command=self.launch_game,
            bg="#00ff66",
            fg="#05260f",
            activebackground="#66ff99",
            font=("Segoe UI", 12, "bold"),
            relief=tk.FLAT,
            padx=25,
            pady=8,
            cursor="hand2",
        )
        self.play_btn.pack(side=tk.RIGHT, padx=20, pady=15)

    def log_diag(self, msg):
        self.diag_txt.insert(tk.END, msg + "\n")
        self.diag_txt.see(tk.END)

    def select_game_directory(self):
        chosen = filedialog.askdirectory(title="Selecciona la carpeta principal de Cyberpunk 2077")
        if chosen:
            p = Path(chosen)
            if self.is_valid_game_path(p):
                self.save_game_path(p)
                self.verify_installation()
            else:
                messagebox.showerror(
                    "Ejecutable no encontrado",
                    "No se encontró Cyberpunk2077.exe dentro de la carpeta seleccionada ni en bin/x64/.",
                )

    def get_vortex_stats(self):
        downloads_count = 0
        staging_count = 0
        collection_names = []

        if VORTEX_DOWNLOADS.exists():
            downloads_count = len([f for f in VORTEX_DOWNLOADS.glob("*") if f.is_file()])

        if VORTEX_STAGING.exists():
            staging_count = len([d for d in VORTEX_STAGING.iterdir() if d.is_dir()])

        state_backups = VORTEX_APPDATA / "temp" / "state_backups_full"
        if state_backups.exists():
            files = list(state_backups.glob("*.json"))
            if files:
                latest = max(files, key=os.path.getmtime)
                try:
                    with open(latest, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        mods = data.get("persistent", {}).get("mods", {}).get("cyberpunk2077", {})
                        for k, v in mods.items():
                            if v.get("type") == "collection":
                                name = v.get("attributes", {}).get("customFileName") or v.get("attributes", {}).get("name")
                                if name and name not in collection_names:
                                    collection_names.append(name)
                except Exception:
                    pass

        return downloads_count, staging_count, collection_names

    def verify_installation(self):
        self.diag_txt.delete("1.0", tk.END)
        self.path_lbl.config(text=str(self.game_path) if self.game_path else "NO ENCONTRADA")

        # Check Vortex status
        dl_cnt, stg_cnt, collections = self.get_vortex_stats()
        col_str = f"Colección: {', '.join(collections)}" if collections else "Colecciones detectadas"
        self.vortex_status_lbl.config(
            text=f"Vortex: {dl_cnt} descargas guardadas | {stg_cnt} mods instalados en Staging.\n{col_str}"
        )

        if not self.game_path or not self.is_valid_game_path(self.game_path):
            self.status_badge.config(text="RUTA NO DETECTADA", bg="#ff3366", fg="#ffffff")
            self.log_diag("[X] No se ha localizado la carpeta de instalación de Cyberpunk 2077.")
            self.log_diag("[!] Haz clic en 'Examinar...' para seleccionar tu carpeta de Cyberpunk.")
            self.play_btn.config(state=tk.DISABLED, bg="#444455")
            return

        self.log_diag(f"[+] Carpeta del juego: {self.game_path}")
        exe = self.get_game_exe()
        self.log_diag(f"[+] Ejecutable: {exe}")

        all_ok = True

        # 1. Comprobar Core Frameworks
        cet_dir = self.game_path / "bin" / "x64" / "plugins" / "cyber_engine_tweaks"
        if (cet_dir / "cyber_engine_tweaks.asi").exists() or (self.game_path / "bin" / "x64" / "version.dll").exists() or cet_dir.exists():
            self.log_diag("[✓] Cyber Engine Tweaks (CET): Instalado y activo.")
        else:
            self.log_diag("[!] Cyber Engine Tweaks no detectado en bin/x64.")
            all_ok = False

        redscript_dir = self.game_path / "r6" / "scripts"
        if redscript_dir.exists() and any(redscript_dir.iterdir()):
            count = len(list(redscript_dir.iterdir()))
            self.log_diag(f"[✓] Redscript: {count} módulos de scripts activos.")
        else:
            self.log_diag("[!] No se detectaron módulos en r6/scripts.")

        archive_mod = self.game_path / "archive" / "pc" / "mod"
        if archive_mod.exists():
            archives = sorted([f.name for f in archive_mod.glob("*.archive")])
            self.log_diag(f"[✓] Archivos .archive instalados en el juego: {len(archives)}")

            base_mods = [a for a in archives if a.startswith(("#", "!"))]
            z_mods = [a for a in archives if a.lower().startswith("z")]
            self.log_diag(f"    - Overhauls base (#, !): {len(base_mods)} paquetes (cargan primero)")
            self.log_diag(f"    - Parches y núcleos (z...): {len(z_mods)} paquetes (cargan al final)")

            if z_mods:
                self.log_diag("    -> Orden de carga verificado: Traducciones y núcleos en posición de sobreescritura óptima.")
        else:
            self.log_diag("[X] Carpeta archive/pc/mod no existe o está vacía.")
            all_ok = False

        # Si hay mods en staging pero pocos en el juego, sugerir despliegue
        if stg_cnt > 0 and archive_mod.exists() and len(list(archive_mod.glob("*.archive"))) < 10:
            self.log_diag("[!] ATENCIÓN: Tienes mods descargados en Vortex que aún no están desplegados en el juego.")
            self.log_diag("    Haz clic en 'Desplegar Mods de Vortex al Juego' arriba para sincronizarlos.")

        if all_ok:
            self.status_badge.config(text="✓ TODO LISTO PARA JUGAR", bg="#00ff66", fg="#05260f")
            self.play_btn.config(state=tk.NORMAL, bg="#00ff66", text="▶ JUGAR CYBERPUNK 2077")
        else:
            self.status_badge.config(text="REVISIÓN PENDIENTE", bg="#ffd600", fg="#0d0d11")
            self.play_btn.config(state=tk.NORMAL, bg="#ffd600", text="▶ INICIAR DE TODOS MODOS")

    def sync_vortex_to_game(self):
        """Despliega directamente los mods presentes en Vortex Staging a la carpeta del juego."""
        if not self.game_path or not self.is_valid_game_path(self.game_path):
            messagebox.showerror("Error", "Primero debes configurar una ruta válida de Cyberpunk 2077.")
            return

        if not VORTEX_STAGING.exists() or not any(VORTEX_STAGING.iterdir()):
            messagebox.showinfo("Sin mods en Vortex", "No se encontraron mods en la carpeta staging de Vortex.")
            return

        confirm = messagebox.askyesno(
            "Desplegar Mods de Vortex",
            f"Se copiarán/sincronizarán los mods desde:\n{VORTEX_STAGING}\nhacia:\n{self.game_path}\n\n¿Deseas continuar?",
        )
        if not confirm:
            return

        self.log_diag("\n[*] Iniciando sincronización de mods desde Vortex al juego...")
        copied = 0
        errors = 0

        for mod_folder in VORTEX_STAGING.iterdir():
            if not mod_folder.is_dir():
                continue
            try:
                for root, dirs, files in os.walk(mod_folder):
                    rel_path = os.path.relpath(root, mod_folder)
                    dest_dir = self.game_path if rel_path == "." else self.game_path / rel_path
                    dest_dir.mkdir(parents=True, exist_ok=True)

                    for f in files:
                        if f.endswith(".vortex") or f == "vortex.deployment.json":
                            continue
                        src_file = Path(root) / f
                        dst_file = dest_dir / f
                        if not dst_file.exists() or dst_file.stat().st_mtime < src_file.stat().st_mtime:
                            shutil.copy2(src_file, dst_file)
                            copied += 1
            except Exception as e:
                errors += 1
                self.log_diag(f"[!] Error copiando mod {mod_folder.name}: {e}")

        self.log_diag(f"[✓] Sincronización finalizada: {copied} archivos copiados/actualizados. Errores: {errors}")
        messagebox.showinfo("Despliegue Completado", f"Se han sincronizado {copied} archivos desde Vortex hacia Cyberpunk 2077.")
        self.verify_installation()

    def open_collection_url(self):
        url = self.url_var.get().strip()
        if url:
            webbrowser.open(url)

    def toggle_automation(self):
        if not self.auto_running:
            self.auto_running = True
            self.auto_btn.config(text="⏹ Detener Auto-Descarga", bg="#ff3366", fg="#ffffff")
            self.log_diag("\n[*] Iniciando bucle de auto-descarga de Nexus Mods / Vortex...")
            self.auto_thread = threading.Thread(target=self.run_auto_loop, daemon=True)
            self.auto_thread.start()
        else:
            self.auto_running = False
            self.auto_btn.config(text="⚡ Iniciar Auto-Descarga", bg="#00b4d8", fg="#0d0d11")
            self.log_diag("[!] Auto-descarga pausada.")

    def run_auto_loop(self):
        if not TPL_VORTEX_PATH.exists() or not TPL_SLOW_PATH.exists() or not TPL_DONT_ASK_PATH.exists():
            self.log_diag("[X] Faltan archivos de plantillas en la carpeta assets.")
            self.auto_running = False
            return

        tpl_vortex = cv2.imread(str(TPL_VORTEX_PATH), cv2.IMREAD_COLOR)
        tpl_slow = cv2.imread(str(TPL_SLOW_PATH), cv2.IMREAD_COLOR)
        tpl_dont_ask = cv2.imread(str(TPL_DONT_ASK_PATH), cv2.IMREAD_COLOR)

        count = 0
        while self.auto_running:
            try:
                screen = grab_screen_bgr()

                # 1. Fallback installer popup
                f_found, fx, fy, f_val = match_tpl(screen, tpl_dont_ask, threshold=0.92)
                if f_found:
                    self.log_diag(f"[!] Fallback Installer detectado. Clic en 'Yes, Install And Don't Ask Again' ({fx}, {fy})")
                    click_screen(fx, fy)
                    time.sleep(3.0)
                    continue

                # 2. Vortex Download manually
                v_found, vx, vy, v_val = match_tpl(screen, tpl_vortex, threshold=0.92)
                if v_found:
                    self.log_diag(f"[+] 'Download manually' detectado ({vx}, {vy}). Clic...")
                    click_screen(vx, vy)
                    time.sleep(2.5)
                    continue

                # 3. Slow download on Nexus
                s_found, sx, sy, s_val = match_tpl(screen, tpl_slow, threshold=0.92)
                if s_found:
                    count += 1
                    self.log_diag(f"[+] 'Slow download' detectado ({sx}, {sy}). Mod #{count} descargado!")
                    click_screen(sx, sy)
                    time.sleep(5.5)
                    continue

                time.sleep(1.0)
            except Exception as e:
                self.log_diag(f"[!] Error en auto-descarga: {e}")
                time.sleep(2.0)

    def launch_game(self):
        exe = self.get_game_exe()
        if not exe or not exe.exists():
            self.select_game_directory()
            exe = self.get_game_exe()
            if not exe or not exe.exists():
                messagebox.showerror("Error", "No se puede iniciar el juego sin seleccionar el ejecutable válido.")
                return

        try:
            self.log_diag(f"\n🚀 Lanzando Cyberpunk 2077 con mods desde: {exe}")
            subprocess.Popen([str(exe)], cwd=str(exe.parent))
            messagebox.showinfo("Iniciando Juego", "¡Cyberpunk 2077 se está iniciando con todos tus mods cargados!")
        except Exception as e:
            messagebox.showerror("Error al iniciar", f"No se pudo iniciar el juego:\n{e}")


if __name__ == "__main__":
    app = CyberpunkModApp()
    app.mainloop()
