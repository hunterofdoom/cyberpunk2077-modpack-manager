# 🎮 Cyberpunk 2077 - Modpack Auto-Manager & Launcher

> **¿Eres nuevo moddeando o solo quieres jugar sin complicaciones?**  
> ¡Has llegado al lugar correcto! Esta herramienta hace todo el trabajo pesado por ti: descarga colecciones de mods de Nexus Mods / Vortex automáticamente sin tener que hacer 150 clics a mano, verifica que los mods no tengan conflictos y lanza Cyberpunk 2077 listo para jugar.

---

## ⚡ Descarga e Inicio Rápido (Releases)

Para empezar a usar la herramienta sin configurar nada técnico:

1. **Descarga la última versión**:
   - Ve al apartado de [Releases de GitHub](https://github.com/hunterofdoom/cyberpunk2077-modpack-manager/releases) y descarga el archivo comprimido **`Cyberpunk2077-Modpack-Manager-v1.0.0.zip`**.
2. **Descomprime el archivo**:
   - Extrae la carpeta en el lugar que prefieras de tu ordenador.
3. **Ejecuta con un solo clic**:
   - Haz doble clic sobre el archivo:
     👉 **`INICIAR_MOD_MANAGER.bat`**
   - El script verificará tu entorno automáticamente, instalará lo necesario de fondo si hace falta y abrirá la ventana gráfica del programa de inmediato.

---

## 🖥️ Cómo Gestionar Cualquier Colección de Mods

Una vez abierta la aplicación, el proceso es completamente intuitivo:

1. **Detectar o Cambiar Carpeta de Cyberpunk 2077**:
   - En la parte superior verás la ruta de tu juego detectada automáticamente (Steam, GOG o personalizada).
   - Si tu juego está en otra carpeta o disco, pulsa **`📂 Cambiar Carpeta...`** y selecciona la carpeta raíz de tu juego. Se guardará para siempre.
2. **Descargar una Colección de Mods**:
   - Pega la URL de la colección de Nexus Mods que quieras instalar (o deja la predeterminada `xyz-spanish`).
   - Pulsa **`Abrir Colección`** para abrirla en Vortex.
   - Pulsa **`⚡ Auto-Descargar Mods`**. La aplicación se encargará de realizar todos los clics de *"Download manually"* y *"Slow download"* de forma desatendida y resolverá avisos automáticamente hasta que termine.
3. **Sincronizar Mods si ya los descargaste**:
   - Si ya descargaste mods con Vortex, pulsa **`📥 Sincronizar Mods a Cyberpunk`** para transferir todos los archivos directamente a tu juego sin tener que volver a descargarlos.
4. **¡A jugar!**:
   - Cuando el estado indique **`✓ TODO LISTO PARA JUGAR`**, haz clic en el botón verde **`▶ JUGAR CYBERPUNK 2077`**.

---

## 📋 ¿Cómo funciona por dentro?

- **Auto-descarga inteligente (Visión por Computador)**:  
  Nexus Mods exige a las cuentas gratuitas pulsar *"Download manually"* en Vortex y *"Slow download"* en el navegador para cada mod. Esta aplicación utiliza visión artificial con OpenCV (`matchTemplate` en espacio RGB) para detectar los botones en pantalla y hacer clic automáticamente, resolviendo también los avisos del instalador de respaldo (*Fallback Installer*) sin interrupciones.
- **Sincronización con Vortex en 1 Clic**:  
  Detecta si tus mods ya están en la carpeta de staging de Vortex (`%APPDATA%\Vortex\cyberpunk2077\mods`) y los copia directamente a las rutas oficiales del motor (`archive\pc\mod`, `r6\scripts`, `r6\tweaks`, `bin\x64\plugins`).
- **Verificador de Compatibilidad y Orden Alfanumérico**:  
  En Cyberpunk 2077 (**REDengine 4**), los archivos `.archive` se cargan en orden alfabético estricto:
  - Archivos con prefijos `#` o `!` (overhauls base de texturas e iluminación) se cargan primero.
  - Archivos con prefijo `z` (traducciones al español y parches de misiones) se cargan al final con máxima prioridad de sobreescritura para evitar textos rotos o bugs.
- **Lanzador Directo sin errores de elevación**:  
  Detecta si Windows requiere elevación de usuario y arranca el juego directamente evitando el molesto error `[WinError 740]`.

---

## 🛠️ Solución a Fallos Comunes (Preguntas Frecuentes)

### 1. "Al pulsar Jugar salía: `[WinError 740] La operación solicitada requiere elevación`"
- **Por qué ocurre**: Windows o un lanzador previo activó la casilla *"Ejecutar como administrador"* en el archivo `Cyberpunk2077.exe`.
- **Cómo lo soluciona este programa**: El lanzador incluye un bypass automático por API nativa de Windows (`ShellExecuteW`). Para quitarlo permanentemente, ve a `bin\x64\Cyberpunk2077.exe` > Clic derecho > **Propiedades** > pestaña **Compatibilidad** > desmarca **"Ejecutar este programa como administrador"**.

### 2. "Al instalar extensiones en Vortex salía: `Cannot find module '@nexusmods/vortex-api'`"
- **Por qué ocurre**: Versiones recientes de extensiones descargadas de Nexus Mods intentan llamar al nuevo paquete `@nexusmods/vortex-api`, mientras que instalaciones existentes de Vortex exponen internamente `vortex-api`.
- **Cómo solucionarlo**: Abre la carpeta `%APPDATA%\Vortex\plugins\Vortex Extension Update - Cyberpunk 2077` y elimina esa carpeta para que Vortex use su extensión nativa integrada, o crea el alias en `node_modules`.

### 3. "El auto-descargador no hace clic en los botones de descarga"
- **Por qué ocurre**: La ventana de Vortex o la pestaña de Nexus Mods en el navegador están minimizadas o tapadas por otra ventana.
- **Cómo solucionarlo**: Deja en pantalla visible la ventana de Vortex y tu navegador (puedes ponerlas una al lado de la otra). El sistema utiliza visión por pantalla y necesita ver los botones para hacer clic.

### 4. "No se encontró Cyberpunk2077.exe dentro de la carpeta seleccionada"
- **Cómo solucionarlo**: En la aplicación, haz clic en **`📂 Cambiar Carpeta...`** y selecciona la carpeta principal de tu Cyberpunk 2077. El programa buscará automáticamente el ejecutable en su interior.

---

## 📄 Licencia
Distribuido bajo la Licencia MIT. Código abierto y libre para la comunidad.
