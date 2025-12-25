# OctoFilament – Documentación para desarrolladores

Este documento describe la arquitectura interna del plugin, el flujo de ejecución, las decisiones de diseño y las partes que pueden modificarse en el futuro.  
Su objetivo es facilitar el mantenimiento del plugin y permitir que otros desarrolladores contribuyan sin necesidad de estudiar todo el código desde cero.

---

## 📁 Estructura del proyecto

octoprint_octofilament/
init.py
octofilament.py
static/
css/
js/
templates/
octofilament_settings.jinja2
setup.py
MANIFEST.in
README.md
LICENSE
DEVELOPERS.md

---

OctoFilament/
├── README.md
├── LICENSE
├── DEVELOPERS.md
├── MANIFEST.in
├── setup.py
│
├── octoprint_octofilament/
│   ├── __init__.py
│   ├── octofilament.py
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── octofilament.css
│   │   └── js/
│   │       └── octofilament.js
│   │
│   └── templates/
│       └── octofilament_settings.jinja2
│
└── (otros archivos opcionales)


---

## 🧠 Arquitectura general

OctoFilament sigue la estructura estándar de un plugin de OctoPrint:

- `__init__.py`  
  Registra la clase principal del plugin y expone los metadatos.

- `octofilament.py`  
  Contiene la lógica principal:
  - Inicialización del GPIO
  - Lectura del estado del sensor
  - Gestión de eventos (pausar/reanudar)
  - Manejo de la configuración
  - Hooks de OctoPrint

- `templates/`  
  Plantillas Jinja2 para la interfaz de usuario en el panel de Settings.

- `static/`  
  Archivos JS/CSS para la interfaz.

- `setup.py`  
  Metadatos del plugin, dependencias, licencia y registro.

---

## ⚙️ Flujo de funcionamiento

1. **Carga del plugin**  
   OctoPrint importa `__init__.py`, que registra la clase `OctoFilamentPlugin`.

2. **Inicialización**  
   En `on_after_startup()`:
   - Se lee la configuración guardada.
   - Se inicializa el pin GPIO.
   - Se registra un callback para detectar cambios de estado.

3. **Monitorización del sensor**  
   El plugin escucha cambios en el pin configurado:
   - Si el estado indica *ausencia de filamento*, se ejecuta `self._printer.pause_print()`.
   - Si vuelve a detectarse filamento y la opción está activada, se ejecuta `self._printer.resume_print()`.

4. **Interfaz de usuario**  
   - La plantilla `octofilament_settings.jinja2` muestra los ajustes.
   - El JS asociado envía/recibe datos mediante los helpers oficiales de OctoPrint.

---

## 🔌 GPIO y lógica del sensor

### Pin por defecto  
`GPIO4` (BCM)

### Lógica por defecto  
`LOW` = filamento presente  
`HIGH` = filamento ausente

Esto se puede cambiar desde la configuración.

### Notas técnicas
- El plugin usa `RPi.GPIO` o `gpiozero` según disponibilidad.
- El pin se configura como entrada con pull-up o pull-down según la lógica seleccionada.
- Se usa `add_event_detect()` para evitar bucles de polling.

---

## 🛠️ Configuración

La configuración se almacena en:

~/.octoprint/config.yaml


---

## 🧩 Hooks utilizados

- `octoprint.plugin.StartupPlugin`
- `octoprint.plugin.SettingsPlugin`
- `octoprint.plugin.TemplatePlugin`
- `octoprint.plugin.AssetPlugin`

---

## 🧪 Pruebas recomendadas

1. **Prueba de arranque**
   - Reiniciar OctoPrint y verificar que el plugin inicializa el GPIO sin errores.

2. **Prueba de pausa**
   - Simular ausencia de filamento (cambiar el estado del pin).
   - Confirmar que la impresión se pausa.

3. **Prueba de reanudación**
   - Restaurar el estado del sensor.
   - Confirmar que la impresión se reanuda si la opción está activada.

4. **Prueba de interfaz**
   - Cambiar ajustes desde Settings.
   - Verificar que se guardan y aplican correctamente.

---

## 🧱 Decisiones de diseño

- **Uso de helpers oficiales de OctoPrint**  
  Evita dependencias rotas y asegura compatibilidad futura.

- **GPIO configurable**  
  Permite adaptarse a cualquier sensor o placa.

- **Lógica configurable**  
  Soporta sensores normalmente abiertos o cerrados.

- **Código minimalista**  
  El plugin hace solo una cosa y la hace bien.

---

## 🚀 Ideas futuras

- Añadir soporte para múltiples sensores.  
- Añadir notificaciones (Telegram, email, etc.).  
- Añadir un contador de pausas por falta de filamento.  
- Añadir un modo “debug” con logs detallados.

---

## 👤 Autor

Desarrollado por Alfonso (alfonsvv).  
Licencia: **AGPLv3**.



