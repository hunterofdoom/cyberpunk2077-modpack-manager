# Cyberpunk 2077 - Modpack Auto-Manager & Launcher 🚀

Herramienta gráfica (GUI) e intuitiva para Windows diseñada para automatizar la descarga de colecciones de Nexus Mods / Vortex, validar la integridad del modpack, verificar el orden de carga y compatibilidad alfanumérica, y lanzar el juego directamente.

---

## 🌟 Características principales

1. **Auto-Descargador de Colecciones Vortex / Nexus Mods**:
   - Introduce la URL de cualquier colección de Cyberpunk 2077.
   - Detección inteligente por visión por computador (OpenCV Template Matching) en color RGB.
   - Hace clic automáticamente en:
     - Botón `Download manually` de Vortex.
     - Botón `Slow download` en la página de Nexus Mods.
     - Resuelve automáticamente los avisos de **Fallback Installer** seleccionando `Yes, Install And Don't Ask Again` para no interrumpir el flujo.

2. **Diagnóstico y Verificación de Compatibilidad**:
   - Comprueba la presencia de frameworks esenciales: **Cyber Engine Tweaks (CET)**, **Redscript**, **ArchiveXL**, **TweakXL**, **Codeware**.
   - Analiza el orden alfanumérico estricto del motor REDengine 4 en `archive\pc\mod\`:
     - Archivos base (`#`, `!`) cargados en primer lugar sin solapar.
     - Parches y traducciones críticas (`z...`) cargadas al final para sobreescritura correcta.
   - Muestra el estado en tiempo real: **`✓ TODO LISTO PARA JUGAR`**.

3. **Detección Automática y Selector de Directorio**:
   - Detecta automáticamente las instalaciones de Steam, GOG o carpetas personalizadas (como `C:\Users\Audur\Desktop\Games NVM\Cyberpunk 2077`).
   - Si no se encuentra o cambias de ruta, se abre un explorador de carpetas y localiza de forma automática `bin\x64\Cyberpunk2077.exe`.

4. **Lanzador Directo**:
   - Botón **`▶ JUGAR CYBERPUNK 2077`** que arranca el juego con el entorno de mods completamente inicializado.

---

## 🛠️ Requisitos e Instalación

### Requisitos previos
- Windows 10 u 11 (64-bit).
- Python 3.10 o superior (instalado con Tkinter).
- Dependencias de Python:
  ```bash
  pip install opencv-python Pillow numpy
  ```

---

## 🚀 Instrucciones de Uso

1. **Iniciar la aplicación**:
   Ejecuta el archivo principal mediante PowerShell o terminal:
   ```powershell
   python cp2077_mod_manager.py
   ```

2. **Descargar una Colección**:
   - Pega la URL de la colección de Nexus Mods en el campo de texto (por defecto incluye `xyz-spanish`).
   - Pulsa **`Abrir Colección`** para abrirla en Vortex / Navegador.
   - Pulsa **`⚡ Iniciar Auto-Descarga`**: la herramienta gestionará los clics de Vortex y Nexus Mods de forma continua hasta completar todos los archivos.

3. **Verificar y Jugar**:
   - La sección de diagnóstico listará los frameworks, número de `.archive` instalados y el estado del orden de carga.
   - En cuanto aparezca el badge verde **`✓ TODO LISTO PARA JUGAR`**, haz clic en **`▶ JUGAR CYBERPUNK 2077`**.
   - Si moviste el juego, pulsa **`Examinar...`** para seleccionar la carpeta raíz y la aplicación guardará la configuración automáticamente en `cp2077_mod_manager_config.json`.
