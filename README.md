# OctoFilament

Detección de presencia de filamento para OctoPrint utilizando un sensor conectado a GPIO.  
OctoFilament pausa automáticamente la impresión cuando el filamento se agota o se retira.
---

## ✨ Características

- Detección de presencia/ausencia de filamento mediante GPIO.
- Compatible con sensores mecánicos, ópticos o de leva.
- Pausa automática de impresión cuando el filamento desaparece.
- Pin GPIO configurable (por defecto GPIO4).
- Lógica configurable (HIGH/LOW).
- Interfaz limpia y minimalista integrada en OctoPrint.
- Mensajes claros en el registro y en la interfaz.
- Código ligero, mantenible y fácil de extender.

---

## 🛠️ Instalación

### Instalación desde URL (recomendada)

En OctoPrint:

1. Ve a **Settings → Plugin Manager → Get More…**
2. Haz clic en **… from URL**
3. Introduce la URL del paquete:

https://github.com/alfonsvv/OctoFilament/releases/download/v0.3.0/OctoFilament-0.3.0.zip


4. Instala y reinicia OctoPrint.

---

## ⚙️ Configuración

### Parámetros principales

- **GPIO Pin**  
  Pin BCM utilizado para leer el estado del sensor.  
  Valor por defecto: `4`.

- **Lógica del sensor**  
  Define si el sensor indica “filamento presente” con nivel **HIGH** o **LOW**.  
  Valor por defecto: `LOW` (sensor normalmente cerrado).

- **Reanudar automáticamente**  
  Si está activado, OctoFilament reanudará la impresión cuando el filamento vuelva a detectarse.

### Requisitos de hardware

- Raspberry Pi con pines GPIO accesibles.
- Sensor de presencia de filamento (mecánico u óptico).
- Cableado simple:  
  - Señal → GPIO configurado  
  - VCC → 3.3V  
  - GND → GND

---

## 📡 Funcionamiento

1. El plugin monitoriza continuamente el estado del pin GPIO configurado.
2. Cuando detecta ausencia de filamento:
   - Pausa la impresión.
   - Muestra un aviso en OctoPrint.
3. Cuando vuelve a detectarse filamento:
   - Reanuda automáticamente si la opción está activada.
   - Registra el evento en el log.

---

## 🧪 Compatibilidad

- **OctoPrint:** 1.9.x o superior  
- **Python:** 3.7+  
- **Raspberry Pi:** cualquier modelo con GPIO  
- **Sistemas operativos:** Raspberry Pi OS / Debian / derivados

---

## 📁 Estructura del proyecto

octoprint_octofilament/
init.py
octofilament.py
static/
templates/
setup.py
MANIFEST.in
README.md
LICENSE

---

## 🐞 Problemas y soporte

Si encuentras un error o tienes una sugerencia, abre un issue en:

👉 https://github.com/alfonsvv/OctoFilament/issues

---

## 📜 Licencia

Este proyecto está licenciado bajo **AGPLv3 License**.  
Consulta el archivo `LICENSE` para más información.

---

## 🙌 Agradecimientos

Gracias a la comunidad de OctoPrint por su documentación, ejemplos y soporte continuo.



