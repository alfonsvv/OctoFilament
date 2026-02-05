# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# OctoFilament by Alfons
# Detector de rotura/ausencia de filamento para OctoPrint.
#
# Este plugin monitoriza un sensor conectado a un GPIO de la Raspberry Pi.
# Cuando detecta ausencia de filamento durante una impresión:
#   1) Pausa la impresión
#   2) Ejecuta un bloque de GCODE (subida Z + park)
#   3) Opcionalmente, tras un tiempo configurable, ejecuta un segundo bloque
#      de GCODE para apagar la impresora (pausa larga)
#
# El plugin también recuerda la temperatura objetivo del hotend y la cama,
# así como la altura Z antes de la pausa, para restaurarlas al reanudar.
#
# Incluye una opción opcional de "anti‑rebotes" para sensores mecánicos.
# -------------------------------------------------------------------------

from octoprint.events import Events
import octoprint.plugin
import flask
import RPi.GPIO as GPIO
import threading
import time

class OctoFilamentPlugin(octoprint.plugin.StartupPlugin,
                         octoprint.plugin.EventHandlerPlugin,
                         octoprint.plugin.TemplatePlugin,
                         octoprint.plugin.SettingsPlugin,
                         octoprint.plugin.SimpleApiPlugin,
                         octoprint.plugin.AssetPlugin):

    def __init__(self):
        # Últimas temperaturas objetivo antes de la pausa
        self._last_tool_target = 0
        self._last_bed_target = 0

        # Indica si el detector está armado (solo pausa si está armado)
        self._armed = True

        # Estado actual del filamento ("present" / "absent")
        self._filament_status = "unknown"

        # Último estado registrado (para evitar spam de logs)
        self._last_status = None

        # Altura Z antes de ejecutar el GCODE de pausa
        self._last_z = None

    # ---------------------------------------------------------------------
    # Se ejecuta al arrancar OctoPrint
    # Configura el GPIO y lanza el hilo de monitorización
    # ---------------------------------------------------------------------
    def on_startup(self, host, port):
        self._logger.info("[OctoFilament] Plugin inicializado correctamente en el arranque")

        pin = self._settings.get_int(["gpio_pin"])

        # Modo BCM y entrada con pull‑up interno (estable y recomendado)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Hilo que monitoriza el sensor continuamente
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    # ---------------------------------------------------------------------
    # Bucle principal de monitorización del sensor
    # Lee el GPIO cada X segundos y determina si hay filamento o no
    # ---------------------------------------------------------------------
    def _monitor_loop(self):
        interval = self._settings.get_int(["check_interval"])
        pin = self._settings.get_int(["gpio_pin"])
        trigger = self._settings.get(["trigger_state"])

        while True:
            # Si está activado el anti‑rebotes, hacemos 3 lecturas rápidas
            if self._settings.get_boolean(["prevent_bounce"]):
                value = self._read_stable(pin)
            else:
                value = GPIO.input(pin)

            # Interpretación del nivel lógico según la configuración del usuario
            if (trigger == "LOW" and value == GPIO.LOW) or (trigger == "HIGH" and value == GPIO.HIGH):
                self.check_filament("present")
            else:
                self.check_filament("absent")

            time.sleep(interval)

    # ---------------------------------------------------------------------
    # Lectura estable del sensor (anti‑rebotes)
    # Realiza 3 lecturas separadas por 10 ms y solo devuelve HIGH si las 3 lo son
    # ---------------------------------------------------------------------
    def _read_stable(self, pin):
        v1 = GPIO.input(pin)
        time.sleep(0.01)
        v2 = GPIO.input(pin)
        time.sleep(0.01)
        v3 = GPIO.input(pin)
        return GPIO.HIGH if (v1 == v2 == v3 == GPIO.HIGH) else GPIO.LOW

    # ---------------------------------------------------------------------
    # Valores por defecto de configuración del plugin
    # ---------------------------------------------------------------------
    def get_settings_defaults(self):
        return dict(
            LoadUnload_Temperature=240, # Temperatura de carga y descarga de filamento
            gpio_pin=4,                 # GPIO BCM usado para el sensor
            trigger_state="HIGH",       # Nivel lógico que indica ausencia
            check_interval=1,           # Frecuencia de lectura del sensor (segundos)

            # GCODE ejecutado tras pausar (pausa corta)
            post_pause_gcode1=(
                "M83 ; relative extrusion\n"
                "G1 E-5 F300 ; retraction\n"
                "G4 P500 ; wait 0,5s\n"
                "G91 ; relative moves\n"
                "G1 Z30 F300 ; lift 30mm\n"
                "G90 ; absolute moves\n"
                "G1 X110 Y0 F6000 ; park\n"
                ";M104 S170 ; hotend 170º"
            ),
            post_pause_delay1=0,        # Delay ANTES de ejecutar GCODE1

            # GCODE ejecutado tras una pausa larga (apagado)
            post_pause_gcode2=(
                "M104 S0 ; hotend off\n"
                "M140 S0 ; bed off\n"
                "M84 ; motors off"
            ),
            post_pause_delay2=3600,     # Tiempo para considerar "pausa larga"

            enable_debug_logs=False,    # Logs detallados de cambios de estado

            # Anti‑rebotes opcional para sensores mecánicos
            prevent_bounce=False,

            # -------------------------------------------------------------
            # Micro‑retracción configurable al reanudar
            # -------------------------------------------------------------
            enable_resume_retract=True,   # Activar/desactivar micro‑retracción
            resume_retract_mm=2.5,        # mm de retracción al pulsar Resume
            resume_retract_speed=300      # velocidad (mm/min)
        )

    # ---------------------------------------------------------------------
    # Plantillas HTML del plugin (navbar + settings)
    # ---------------------------------------------------------------------
    def get_template_configs(self):
        self._logger.info("[OctoFilament] get_template_configs llamado")
        return [
            dict(type="navbar", name="OctoFilament", template="navbar_plugin_octofilament.jinja2"),
            dict(type="settings", name="OctoFilament", template="settings.jinja2", custom_bindings=False)
        ]

    # ---------------------------------------------------------------------
    # Archivos JS y CSS del plugin
    # ---------------------------------------------------------------------
    def get_assets(self):
        self._logger.info("[OctoFilament] Registrando assets JS/CSS")
        return {
            "js": ["octofilament/octofilament.js", "js/settings.js"],
            "css": ["octofilament/octofilament.css"]
        }

    # ---------------------------------------------------------------------
    # API simple: permite consultar el estado del filamento
    # ---------------------------------------------------------------------
    def on_api_get(self, request):
        return flask.jsonify({"status": self._filament_status})

    def get_api_commands(self):
        return dict()

    def is_api_protected(self):
        return False

    # ---------------------------------------------------------------------
    # Manejo de eventos de OctoPrint (pausa y reanudación)
    # ---------------------------------------------------------------------
    def on_event(self, event, payload):

        # -------------------------------------------------------------
        # EVENTO: PRINT_PAUSED
        # Aquí la impresora YA está pausada y quieta.
        # Es el lugar perfecto para ejecutar GCODE1 sin goteo.
        # -------------------------------------------------------------
        if event == Events.PRINT_PAUSED:

            # Guardar temperaturas objetivo
            temps = self._printer.get_current_temperatures()
            self._last_tool_target = temps.get("tool0", {}).get("target", 0) or 0
            self._last_bed_target = temps.get("bed", {}).get("target", 0) or 0
            self._logger.info(f"[OctoFilament] Pausa: objetivos guardados hotend={self._last_tool_target}, cama={self._last_bed_target}")

            # Guardar altura Z actual
            try:
                current_data = self._printer.get_current_data() or {}
                self._last_z = current_data.get("currentZ", None)
                self._logger.info(f"[OctoFilament] Z actual guardada: {self._last_z}")
            except Exception as e:
                self._logger.info(f"[OctoFilament] No se pudo leer la Z actual: {e}")
                self._last_z = None

            # Ejecutar DELAY1 antes del movimiento (si está configurado)
            d1 = self._settings.get_int(["post_pause_delay1"]) or 0
            if d1 > 0:
                self._logger.info(f"[OctoFilament] Delay1 antes de GCODE1: {d1} segundos...")
                time.sleep(d1)

            # Ejecutar GCODE1 (pausa corta)
            g1 = self._settings.get(["post_pause_gcode1"]) or ""
            if g1.strip():
                self._logger.info("[OctoFilament] Ejecutando GCODE1 tras PRINT_PAUSED...")
                self._printer.commands(g1.split("\n"))

            # Desarmar detector
            self._armed = False

        # -------------------------------------------------------------
        # EVENTO: PRINT_RESUMED
        # Restaurar temperaturas y altura Z original
        # + Micro‑retracción automática para evitar rezumado
        # -------------------------------------------------------------
        elif event == Events.PRINT_RESUMED:

            # ---------------------------------------------------------
            # MICRO‑RETRACCIÓN CONFIGURABLE ANTES DE QUE EL CABEZAL SE MUEVA
            # ---------------------------------------------------------
            # Este GCODE se ejecuta justo al pulsar Resume, antes de que
            # OctoPrint devuelva el cabezal a la pieza. El objetivo es
            # eliminar la gota que se forma mientras el usuario limpia
            # la boquilla durante la pausa.
            #
            # Los valores (mm y velocidad) son configurables desde Settings.
            # Si mm=0 o la función está desactivada, no se ejecuta.
            # ---------------------------------------------------------

            if self._settings.get_boolean(["enable_resume_retract"]):
                mm = float(self._settings.get(["resume_retract_mm"]) or 0)
                speed = int(self._settings.get(["resume_retract_speed"]) or 300)

                if mm > 0:
                    self._logger.info(f"[OctoFilament] Micro‑retracción previa al Resume: {mm}mm @ {speed}mm/min")
                    self._printer.commands([
                        "G91",                     # Modo relativo
                        f"G1 E-{mm} F{speed}",     # Retracción configurable
                        "G90"                      # Volver a modo absoluto
                    ])
                else:
                    self._logger.info("[OctoFilament] Micro‑retracción desactivada (mm=0)")
            else:
                self._logger.info("[OctoFilament] Micro‑retracción desactivada por configuración")


            # Restaurar temperatura del hotend
            if self._last_tool_target and self._last_tool_target > 0:
                self._logger.info(f"[OctoFilament] Resumed: esperando hotend a {self._last_tool_target}°C (M109)")
                self._printer.commands([f"M109 S{int(self._last_tool_target)}"])

            # Restaurar temperatura de la cama
            if self._last_bed_target and self._last_bed_target > 0:
                self._logger.info(f"[OctoFilament] Resumed: ajustando cama a {self._last_bed_target}°C (M140)")
                self._printer.commands([f"M140 S{int(self._last_bed_target)}"])

            # Restaurar altura Z original si estaba guardada
            if self._last_z is not None:
                self._logger.info(f"[OctoFilament] Restaurando Z original: {self._last_z}")
                self._printer.commands([f"G1 Z{self._last_z} F600"])

            # Rearmar detector
            self._armed = True
            self._logger.info("[OctoFilament] Resume completado. Detector rearmado para nuevas pausas.")

    # ---------------------------------------------------------------------
    # Lógica principal de detección de filamento
    # ---------------------------------------------------------------------
    def check_filament(self, status):
        status = status or "unknown"

        # Registrar cambios de estado (solo si cambian)
        if status != self._last_status:
            if self._settings.get_boolean(["enable_debug_logs"]):
                self._logger.info(f"[OctoFilament] Estado de filamento cambiado: {status}")
            self._last_status = status

        self._filament_status = status

        # -------------------------------------------------------------
        # Si no hay filamento y estamos imprimiendo → PAUSA
        # -------------------------------------------------------------
        if status == "absent" and self._armed and self._printer.is_printing():
            self._logger.info("[OctoFilament] Filamento ausente. Pausando impresión...")

            # 1. Pausar impresión (vacía el buffer y garantiza pausa real)
            self._printer.pause_print()

            # 2. NO ejecutar GCODE1 aquí
            #    Ahora se ejecuta en PRINT_PAUSED para evitar goteo

            # 3. Hilo para gestionar pausa larga (GCODE2)
            def _delayed_shutdown():
                d2 = self._settings.get_int(["post_pause_delay2"]) or 0

                if d2 > 0:
                    self._logger.info(f"[OctoFilament] Esperando {d2} segundos antes de posible apagado por pausa larga...")
                    time.sleep(d2)

                    # Si sigue pausado y no se ha rearmado → ejecutar GCODE2
                    if not self._armed and self._printer.is_paused():
                        g2 = self._settings.get(["post_pause_gcode2"]) or ""
                        if g2.strip():
                            self._logger.info("[OctoFilament] Pausa larga detectada. Ejecutando GCODE2...")
                            self._printer.commands(g2.split("\n"))
                    else:
                        self._logger.info("[OctoFilament] Reanudación detectada antes del timeout. GCODE2 no se ejecuta.")

            threading.Thread(target=_delayed_shutdown, daemon=True).start()

        # Si hay filamento → no hacemos nada (evita spam)
        elif status == "present":
            pass
