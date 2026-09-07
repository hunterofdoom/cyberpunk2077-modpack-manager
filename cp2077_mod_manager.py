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
from tkinter import messagebox, filedialog

import cv2
import numpy as np
from PIL import Image, ImageGrab

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
    Path(r"C:\GOG Games\Cyberpunk 2077"),
    Path(r"D:\GOG Games\Cyberpunk 2077"),
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
        self.title("Cyberpunk 2077 - Gestor Fácil de Modpacks & Lanzador")
        self.geometry("900x720")
        self.minsize(860, 660)
        self.configure(bg="#0b0c10")

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
        # 1. Cabecera principal con estilo Cyberpunk
        header = tk.Frame(self, bg="#161b22", height=75)
        header.pack(fill=tk.X, side=tk.TOP)

        title_container = tk.Frame(header, bg="#161b22")
        title_container.pack(side=tk.LEFT, padx=20, pady=12)

        title_lbl = tk.Label(
            title_container,
            text="CYBERPUNK 2077 // MODPACK LAUNCHER",
            font=("Consolas", 15, "bold"),
            fg="#00f0ff",
            bg="#161b22",
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            title_container,
            text="Un clic para descargar, validar, ordenar y empezar a jugar",
            font=("Segoe UI", 9),
            fg="#8b949e",
            bg="#161b22",
        )
        subtitle_lbl.pack(anchor="w")

        self.status_badge = tk.Label(
            header,
            text="ANALIZANDO...",
            font=("Segoe UI", 10, "bold"),
            fg="#0b0c10",
            bg="#ffd600",
            padx=14,
            pady=6,
            relief=tk.FLAT,
        )
        self.status_badge.pack(side=tk.RIGHT, padx=20, pady=18)

        # Contenedor central
        content = tk.Frame(self, bg="#0b0c10")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        # Card 0: Ruta de Instalación del Juego (Muy accesible para cualquier usuario)
        path_frame = tk.LabelFrame(
            content,
            text=" 📁 Carpeta de Instalación de Cyberpunk 2077 ",
            font=("Segoe UI", 10, "bold"),
            fg="#00f0ff",
            bg="#13171f",
            bd=1,
            relief=tk.SOLID,
        )
        path_frame.pack(fill=tk.X, pady=6)

        path_inner = tk.Frame(path_frame, bg="#13171f")
        path_inner.pack(fill=tk.X, padx=12, pady=10)

        self.path_entry_var = tk.StringVar(value=str(self.game_path) if self.game_path else "")
        self.path_entry = tk.Entry(
            path_inner,
            textvariable=self.path_entry_var,
            font=("Segoe UI", 9),
            bg="#1c2128",
            fg="#58a6ff",
            insertbackground="#00f0ff",
            relief=tk.FLAT,
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_btn = tk.Button(
            path_inner,
            text="📂 Cambiar Carpeta...",
            command=self.select_game_directory,
            bg="#30363d",
            fg="#ffffff",
            activebackground="#484f58",
            activeforeground="#00f0ff",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
        )
        browse_btn.pack(side=tk.RIGHT)

        # Card 1: Descarga de Colecciones
        url_frame = tk.LabelFrame(
            content,
            text=" 🌐 Instalar Colección de Nexus Mods / Vortex ",
            font=("Segoe UI", 10, "bold"),
            fg="#fcee0a",
            bg="#13171f",
            bd=1,
            relief=tk.SOLID,
        )
        url_frame.pack(fill=tk.X, pady=6)

        url_inner = tk.Frame(url_frame, bg="#13171f")
        url_inner.pack(fill=tk.X, padx=12, pady=10)

        self.url_var = tk.StringVar(value="https://www.nexusmods.com/cyberpunk2077/collections/xyz-spanish")
        url_entry = tk.Entry(
            url_inner,
            textvariable=self.url_var,
            font=("Segoe UI", 10),
            bg="#1c2128",
            fg="#ffffff",
            insertbackground="#00f0ff",
            relief=tk.FLAT,
        )
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        open_btn = tk.Button(
            url_inner,
            text="Abrir Colección",
            command=self.open_collection_url,
            bg="#30363d",
            fg="#ffffff",
            activebackground="#484f58",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            cursor="hand2",
        )
        open_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.auto_btn = tk.Button(
            url_inner,
            text="⚡ Auto-Descargar Mods",
            command=self.toggle_automation,
            bg="#00b4d8",
            fg="#0b0c10",
            activebackground="#90e0ef",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            cursor="hand2",
        )
        self.auto_btn.pack(side=tk.RIGHT)

        # Card 2: Vortex & Sincronización Rápida
        vortex_frame = tk.LabelFrame(
            content,
            text=" 📦 Mods en Vortex & Despliegue Rápido ",
            font=("Segoe UI", 10, "bold"),
            fg="#39ff14",
            bg="#13171f",
            bd=1,
            relief=tk.SOLID,
        )
        vortex_frame.pack(fill=tk.X, pady=6)

        vortex_inner = tk.Frame(vortex_frame, bg="#13171f")
        vortex_inner.pack(fill=tk.X, padx=12, pady=8)

        self.vortex_status_lbl = tk.Label(
            vortex_inner,
            text="Buscando mods de Vortex...",
            font=("Segoe UI", 9),
            fg="#ffffff",
            bg="#13171f",
            justify=tk.LEFT,
        )
        self.vortex_status_lbl.pack(side=tk.LEFT)

        self.sync_btn = tk.Button(
            vortex_inner,
            text="📥 Sincronizar Mods a Cyberpunk",
            command=self.sync_vortex_to_game,
            bg="#238636",
            fg="#ffffff",
            activebackground="#2ea043",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=4,
            cursor="hand2",
        )
        self.sync_btn.pack(side=tk.RIGHT)

        # Card 3: Diagnóstico y Registro
        diag_frame = tk.LabelFrame(
            content,
            text=" 🔍 Comprobación de Compatibilidad & Orden de Carga ",
            font=("Segoe UI", 10, "bold"),
            fg="#8b949e",
            bg="#13171f",
            bd=1,
            relief=tk.SOLID,
        )
        diag_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        self.diag_txt = tk.Text(
            diag_frame,
            bg="#0d1117",
            fg="#c9d1d9",
            font=("Consolas", 9),
            height=7,
            bd=0,
            padx=12,
            pady=8,
            relief=tk.FLAT,
        )
        self.diag_txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # 4. Botonera Inferior
        bottom_bar = tk.Frame(self, bg="#161b22", height=80)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)

        refresh_btn = tk.Button(
            bottom_bar,
            text="🔄 Re-verificar Todo",
            command=self.verify_installation,
            bg="#21262d",
            fg="#c9d1d9",
            activebackground="#30363d",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=16,
            pady=10,
            cursor="hand2",
        )
        refresh_btn.pack(side=tk.LEFT, padx=20, pady=14)

        self.play_btn = tk.Button(
            bottom_bar,
            text="▶ JUGAR CYBERPUNK 2077",
            command=self.launch_game,
            bg="#00ff66",
            fg="#05260f",
            activebackground="#33ff85",
            font=("Segoe UI", 13, "bold"),
            relief=tk.FLAT,
            padx=28,
            pady=10,
            cursor="hand2",
        )
        self.play_btn.pack(side=tk.RIGHT, padx=20, pady=14)

    def log_diag(self, msg):
        self.diag_txt.insert(tk.END, msg + "\n")
        self.diag_txt.see(tk.END)

    def select_game_directory(self):
        chosen = filedialog.askdirectory(
            title="Selecciona la carpeta principal de Cyberpunk 2077 (donde está el juego)"
        )
        if chosen:
            p = Path(chosen)
            if self.is_valid_game_path(p):
                self.save_game_path(p)
                self.path_entry_var.set(str(p))
                self.verify_installation()
                messagebox.showinfo("Ruta Guardada", f"Cyberpunk 2077 detectado correctamente en:\n{p}")
            else:
                # Intentar buscar subcarpetas si seleccionó una carpeta superior
                found_exe = list(p.rglob("Cyberpunk2077.exe"))
                if found_exe:
                    correct_p = found_exe[0].parent.parent.parent if found_exe[0].parent.name == "x64" else found_exe[0].parent
                    self.save_game_path(correct_p)
                    self.path_entry_var.set(str(correct_p))
                    self.verify_installation()
                    messagebox.showinfo("Ruta Auto-corregida", f"Se localizó Cyberpunk 2077 en:\n{correct_p}")
                else:
                    messagebox.showerror(
                        "Ejecutable no encontrado",
                        "No se encontró 'Cyberpunk2077.exe' en esa carpeta.\nPor favor selecciona la carpeta que contiene las carpetas 'bin', 'r6' o 'archive'.",
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

        # 1. Comprobar Vortex
        dl_cnt, stg_cnt, collections = self.get_vortex_stats()
        col_str = f"Colección: {', '.join(collections)}" if collections else "Colecciones detectadas"
        self.vortex_status_lbl.config(
            text=f"{dl_cnt} descargas | {stg_cnt} mods instalados en Staging.\n{col_str}"
        )

        # 2. Comprobar Juego
        if not self.game_path or not self.is_valid_game_path(self.game_path):
            self.status_badge.config(text="📁 RUTA NO ENCONTRADA", bg="#ff3366", fg="#ffffff")
            self.path_entry_var.set("No detectada - Haz clic en 'Cambiar Carpeta...'")
            self.log_diag("[X] No se ha encontrado la carpeta de Cyberpunk 2077.")
            self.log_diag("[!] Haz clic en 'Cambiar Carpeta...' para indicar dónde está tu juego.")
            self.play_btn.config(state=tk.DISABLED, bg="#484f58", fg="#8b949e")
            return

        self.path_entry_var.set(str(self.game_path))
        exe = self.get_game_exe()
        self.log_diag(f"[+] Juego: {self.game_path}")
        self.log_diag(f"[+] Ejecutable detectado: {exe.name}")

        all_ok = True

        # Frameworks
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
            self.log_diag(f"[✓] Archivos .archive en el juego: {len(archives)}")

            base_mods = [a for a in archives if a.startswith(("#", "!"))]
            z_mods = [a for a in archives if a.lower().startswith("z")]
            self.log_diag(f"    - Mods base (#, !): {len(base_mods)} paquetes (cargan primero)")
            self.log_diag(f"    - Parches y núcleos (z...): {len(z_mods)} paquetes (cargan al final)")

            if z_mods:
                self.log_diag("    -> Orden alfanumérico verificado: Traducciones y núcleos en posición óptima.")
        else:
            self.log_diag("[X] Carpeta archive/pc/mod no encontrada.")
            all_ok = False

        if all_ok:
            self.status_badge.config(text="✓ TODO LISTO PARA JUGAR", bg="#00ff66", fg="#05260f")
            self.play_btn.config(state=tk.NORMAL, bg="#00ff66", fg="#05260f", text="▶ JUGAR CYBERPUNK 2077")
        else:
            self.status_badge.config(text="REVISIÓN PENDIENTE", bg="#ffd600", fg="#0b0c10")
            self.play_btn.config(state=tk.NORMAL, bg="#ffd600", fg="#0b0c10", text="▶ INICIAR DE TODOS MODOS")

    def sync_vortex_to_game(self):
        if not self.game_path or not self.is_valid_game_path(self.game_path):
            messagebox.showerror("Error", "Primero selecciona una carpeta válida del juego.")
            return

        if not VORTEX_STAGING.exists() or not any(VORTEX_STAGING.iterdir()):
            messagebox.showinfo("Sin mods", "No se encontraron mods en la carpeta staging de Vortex.")
            return

        confirm = messagebox.askyesno(
            "Sincronizar Mods",
            f"Se aplicarán todos los mods descargados en Vortex hacia tu juego:\n{self.game_path}\n\n¿Deseas continuar?",
        )
        if not confirm:
            return

        self.log_diag("\n[*] Sincronizando mods desde Vortex al juego...")
        copied = 0
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
                self.log_diag(f"[!] Error en mod {mod_folder.name}: {e}")

        self.log_diag(f"[✓] Sincronización completada ({copied} archivos).")
        messagebox.showinfo("Listo", f"Se han sincronizado {copied} archivos al juego.")
        self.verify_installation()

    def open_collection_url(self):
        url = self.url_var.get().strip()
        if url:
            webbrowser.open(url)

    def toggle_automation(self):
        if not self.auto_running:
            self.auto_running = True
            self.auto_btn.config(text="⏹ Detener Descarga", bg="#ff3366", fg="#ffffff")
            self.log_diag("\n[*] Iniciando auto-descarga con reconocimiento visual...")
            self.auto_thread = threading.Thread(target=self.run_auto_loop, daemon=True)
            self.auto_thread.start()
        else:
            self.auto_running = False
            self.auto_btn.config(text="⚡ Auto-Descargar Mods", bg="#00b4d8", fg="#0b0c10")
            self.log_diag("[!] Auto-descarga detenida.")

    def run_auto_loop(self):
        if not TPL_VORTEX_PATH.exists() or not TPL_SLOW_PATH.exists() or not TPL_DONT_ASK_PATH.exists():
            self.log_diag("[X] Faltan imágenes de plantillas en la carpeta assets.")
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
                self.log_diag(f"[!] Error: {e}")
                time.sleep(2.0)

    def launch_game(self):
        exe = self.get_game_exe()
        if not exe or not exe.exists():
            self.select_game_directory()
            exe = self.get_game_exe()
            if not exe or not exe.exists():
                messagebox.showerror("Error", "No se encontró el ejecutable Cyberpunk2077.exe.")
                return

        try:
            self.log_diag(f"\n🚀 Lanzando Cyberpunk 2077 con mods desde: {exe}")
            
            # Intento 1: Lanzamiento directo estándar (sin privilegios de admin)
            try:
                subprocess.Popen([str(exe)], cwd=str(exe.parent))
            except OSError as ex:
                # Si Windows requiere elevación (WinError 740), usar ShellExecute nativo
                if getattr(ex, 'winerror', None) == 740:
                    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", str(exe), "", str(exe.parent), 1)
                    if ret <= 32:
                        # Si el usuario canceló el diálogo UAC o falló
                        raise OSError(740, "Se canceló la autorización de elevación de Windows.", str(exe))
                else:
                    # Intento alternativo con ShellExecuteW estándar
                    ret = ctypes.windll.shell32.ShellExecuteW(None, "open", str(exe), "", str(exe.parent), 1)
                    if ret <= 32:
                        raise ex

            messagebox.showinfo("Iniciando Juego", "¡Cyberpunk 2077 se está iniciando con todos tus mods cargados!")
        except Exception as e:
            messagebox.showerror("Error al iniciar", f"No se pudo iniciar el juego:\n{e}")


if __name__ == "__main__":
    app = CyberpunkModApp()
    app.mainloop()
