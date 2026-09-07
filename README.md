# 🚀 Cyberpunk 2077 - Modpack Auto-Manager & Launcher

Herramienta gráfica nativa e intuitiva para Windows diseñada para automatizar la descarga de colecciones de Nexus Mods / Vortex, validar la integridad del modpack, verificar el orden de carga y compatibilidad alfanumérica, y lanzar el juego directamente sin complicaciones técnicas.

![Windows](https://img.shields.io/badge/OS-Windows%2010%20%7C%2011-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📋 ¿Cómo funciona?

1. **Auto-descarga sin intervención (Nexus Mods Free Tier)**:
   - Nexus Mods obliga a los usuarios gratuitos a descargar mod por mod pulsando *"Download manually"* en Vortex y *"Slow download"* en el navegador por cada archivo.
   - Esta aplicación integra un motor de visión por computador con OpenCV (`matchTemplate` en espacio RGB) que detecta en tiempo real las ventanas y diálogos de Vortex y Nexus Mods, realizando los clics automáticamente y resolviendo avisos como el instalador de respaldo (*Fallback Installer*).
2. **Detección Automática de Vortex**:
   - Inspecciona el almacenamiento de Vortex (`%APPDATA%\Vortex\cyberpunk2077\mods` y descargas). Si ya descargaste una colección, detecta cuántos mods tienes listos y permite desplegarlos al juego con un solo clic.
3. **Verificación de Compatibilidad y Orden Alfanumérico**:
   - En Cyberpunk 2077 (**REDengine 4**), los mods `.archive` se leen en orden alfanumérico estricto (`#`, `!`, `A-Z`, `z...`). El gestor verifica que los overhauls base carguen primero y que los parches, textos y traducciones críticas carguen al final con máxima prioridad de sobreescritura.
4. **Lanzamiento con 1 Clic**:
   - Detecta automáticamente el ejecutable `Cyberpunk2077.exe` en cualquier disco (Steam, GOG o personalizado) y lo inicia directamente.

---

## ⚡ Inicio Rápido (Para Usuarios)

### 1. Requisitos Previos
Tener instalado **Python 3.10 o superior** con las librerías necesarias:
```powershell
pip install opencv-python Pillow numpy
```

### 2. Ejecutar la Aplicación
Simplemente haz **doble clic en**:
```text
INICIAR_MOD_MANAGER.bat
```
*(No requiere abrir consolas ni escribir comandos).*

---

## 🖥️ Guía de Uso Paso a Paso

1. **Seleccionar Carpeta del Juego**:
   - La aplicación detectará automáticamente tu instalación si está en Steam, GOG o en tu Escritorio.
   - Si tienes el juego en otra ruta, pulsa **`📂 Cambiar Carpeta...`** y selecciona la carpeta raíz de Cyberpunk 2077 (la que contiene `bin`, `r6`, `archive`). La ruta se guardará para siempre.
2. **Descargar una Colección de Mods**:
   - Pega el enlace de la colección de Nexus Mods en el campo de texto (por defecto viene con `xyz-spanish`).
   - Pulsa **`Abrir Colección`** para inicializar la colección en Vortex.
   - Pulsa **`⚡ Auto-Descargar Mods`**. La aplicación se encargará de gestionar los 150+ clics de Vortex y el navegador por ti.
3. **Sincronizar y Desplegar Mods**:
   - Si los mods ya están en Vortex, pulsa **`📥 Sincronizar Mods a Cyberpunk`** para transferir todos los archivos a la carpeta de tu juego.
4. **Jugar**:
   - Cuando el indicador superior marque **`✓ TODO LISTO PARA JUGAR`**, pulsa el botón verde **`▶ JUGAR CYBERPUNK 2077`**.

---

## 🛠️ Solución de Fallos Comunes (Troubleshooting)

### 1. Error: `Cannot find module '@nexusmods/vortex-api'` al instalar extensiones en Vortex
- **Causa**: Las versiones de Vortex pueden tener discrepancias de nombres entre la API empaquetada (`vortex-api`) y los nuevos módulos descargados desde Nexus Mods (`@nexusmods/vortex-api`).
- **Solución**:
  - Cierra Vortex.
  - Ve a `%APPDATA%\Vortex\plugins\Vortex Extension Update - Cyberpunk 2077\node_modules\@nexusmods\vortex-api`.
  - Asegúrate de que apunte internamente a `module.exports = require('vortex-api');` o elimina la carpeta descargada en `%APPDATA%\Vortex\plugins\` para que Vortex use su extensión nativa integrada.

### 2. Error: `[WinError 740] La operación solicitada requiere elevación` al pulsar Jugar
- **Causa**: `Cyberpunk2077.exe` tiene activada la casilla de compatibilidad *"Ejecutar este programa como administrador"* en Windows, impidiendo que procesos estándar de usuario lo ejecuten directamente.
- **Solución**:
  - Nuestra aplicación ya incluye fallback automático por `ShellExecuteW` con elevación segura.
  - Para quitar el bloqueo permanentemente: Haz clic derecho en `bin\x64\Cyberpunk2077.exe` > **Propiedades** > pestaña **Compatibilidad** > desmarca **"Ejecutar este programa como administrador"**.

### 3. El auto-descargador no hace clic en los botones
- **Causa**: Las ventanas de Vortex o del navegador están minimizadas o tapadas por otra aplicación.
- **Solución**: Mantén tanto la ventana de Vortex como la pestaña de Nexus Mods en pantalla visible mientras esté activada la auto-descarga. El sistema utiliza reconocimiento visual por plantilla sobre lo que se muestra en pantalla.

### 4. `No se encontró Cyberpunk2077.exe dentro de la carpeta`
- **Causa**: Se seleccionó una carpeta incorrecta o una subcarpeta como `bin`.
- **Solución**: En la aplicación, pulsa **`📂 Cambiar Carpeta...`** y selecciona la carpeta raíz principal del juego (por ejemplo, `C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077` o tu carpeta de instalación en disco). El buscador inteligente localizará el ejecutable dentro de `bin\x64\`.

---

## 📄 Licencia
Distribuido bajo la Licencia MIT. Consulta `LICENSE` para más información.
