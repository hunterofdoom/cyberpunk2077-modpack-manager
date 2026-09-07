# 🎮 Cyberpunk 2077 - Modpack Auto-Manager & Launcher

> **¿Eres nuevo moddeando o solo quieres jugar sin complicaciones?**  
> ¡Has llegado al lugar correcto! Esta herramienta hace todo el trabajo pesado por ti: se encarga de descargar las colecciones de mods de Nexus Mods / Vortex automáticamente sin que tengas que pulsar 150 veces, comprueba que los mods no se peleen entre sí y lanza tu juego con un solo clic.

---

## ⚡ Guía Ultra-Rápida (Empieza en 3 Pasos)

Si nunca has usado esta herramienta o no quieres liarte con consolas, sigue estos pasos:

1. **Instala los requisitos (solo la primera vez)**:
   Abre una consola (PowerShell o CMD) y escribe:
   ```powershell
   pip install opencv-python Pillow numpy
   ```
2. **Abre el programa con un clic**:
   Haz doble clic sobre el archivo:
   👉 **`INICIAR_MOD_MANAGER.bat`**  
   *(Se abrirá la ventana gráfica automáticamente sin tocar nada más).*

3. **¡A jugar!**:
   - Comprueba que la barra de arriba muestre tu carpeta del juego (si no la detecta, pulsa **`📂 Cambiar Carpeta...`** y elige dónde está instalado Cyberpunk).
   - Si ya descargaste los mods en Vortex, pulsa **`📥 Sincronizar Mods a Cyberpunk`**.
   - En cuanto veas el botón verde **`✓ TODO LISTO PARA JUGAR`**, haz clic en **`▶ JUGAR CYBERPUNK 2077`**.

---

## 📋 ¿Cómo funciona por dentro?

- **Auto-descarga sin pulsar 150 veces**:  
  Nexus Mods exige a las cuentas gratuitas pulsar *"Download manually"* en Vortex y *"Slow download"* en el navegador para cada mod. Esta aplicación utiliza visión artificial inteligente (OpenCV Template Matching en color RGB) para detectar los botones y hacer clic por ti hasta que termine la colección completa, resolviendo avisos molestos como el instalador de respaldo (*Fallback Installer*) automáticamente.
- **Sincronización con Vortex en 1 Clic**:  
  Detecta si tus mods ya están descargados en tu equipo (`%APPDATA%\Vortex`) y los copia directamente a las carpetas correctas de Cyberpunk 2077 (`archive`, `bin`, `r6`, `mods`).
- **Verificador de Compatibilidad y Orden Alfanumérico**:  
  En Cyberpunk 2077 (**REDengine 4**), los mods se leen en orden alfabético estricto:
  - Archivos con prefijos `#` o `!` (overhauls base de texturas e iluminación) cargan primero.
  - Archivos con prefijo `z` (traducciones al español y parches críticos) cargan al final para sobreescribir con máxima prioridad y que el juego esté en español sin errores.
- **Lanzador Directo sin elevación**:  
  Arranca el juego detectando si tu Windows requiere permisos especiales o arranque normal, evitando bloqueos y errores de permisos.

---

## 🛠️ Solución a Fallos Comunes (Preguntas Frecuentes)

### 1. "Al pulsar Jugar me salía: `[WinError 740] La operación solicitada requiere elevación`"
- **Por qué ocurre**: Windows o algún lanzador previo marcó la casilla "Ejecutar como administrador" en el archivo `Cyberpunk2077.exe`.
- **Cómo lo soluciona este programa**: El lanzador incluye un bypass automático nativo (`ShellExecuteW`), pero si prefieres desactivarlo manualmente: ve a la carpeta del juego `bin\x64\Cyberpunk2077.exe` > Clic derecho > **Propiedades** > pestaña **Compatibilidad** > desmarca **"Ejecutar este programa como administrador"**.

### 2. "Al instalar extensiones en Vortex salía: `Cannot find module '@nexusmods/vortex-api'`"
- **Por qué ocurre**: Versiones recientes de extensiones descargadas de Nexus Mods intentan llamar al nuevo paquete `@nexusmods/vortex-api`, mientras que instalaciones existentes de Vortex exponen internamente `vortex-api`.
- **Cómo solucionarlo**: Abre la carpeta `%APPDATA%\Vortex\plugins\Vortex Extension Update - Cyberpunk 2077` y elimina esa carpeta descargada para que Vortex use su extensión nativa integrada, o añade el alias en `node_modules`.

### 3. "El auto-descargador no hace clic en los botones de descarga"
- **Por qué ocurre**: La ventana de Vortex o la pestaña de Nexus Mods en el navegador están minimizadas o tapadas por otra ventana en pantalla completa.
- **Cómo solucionarlo**: Deja en pantalla visible la ventana de Vortex y tu navegador (puedes ponerlas una al lado de la otra). El sistema necesita ver los botones en pantalla para reconocerlos y hacer clic.

### 4. "No se encontró Cyberpunk2077.exe dentro de la carpeta seleccionada"
- **Cómo solucionarlo**: En la aplicación, haz clic en **`📂 Cambiar Carpeta...`** y selecciona la carpeta principal de tu Cyberpunk (la que contiene las carpetas `bin`, `archive`, `r6`). El programa buscará automáticamente el ejecutable en su interior.

---

## 📄 Licencia
Distribuido bajo la Licencia MIT. Código abierto y libre para la comunidad.
