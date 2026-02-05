// ---------------------------------------------------------------------------
// OctoFilament - ViewModel del lado del cliente (JavaScript)
// ---------------------------------------------------------------------------
// Este archivo controla la parte visual del plugin en el navegador:
//
//  - Muestra un icono en la barra superior (navbar)
//  - Consulta periódicamente el estado del filamento vía API
//  - Actualiza el color y el icono según el estado ("present", "absent", etc.)
//  - Se integra con Knockout.js y con el sistema de ViewModels de OctoPrint
//
// No modifica la lógica del servidor; solo muestra información al usuario.
// ---------------------------------------------------------------------------

$(function() {

    // -----------------------------------------------------------------------
    // ViewModel principal del plugin
    // OctoPrint lo instanciará automáticamente al cargar la interfaz web.
    // -----------------------------------------------------------------------
    function OctoFilamentViewModel(parameters) {
        var self = this;

        // ViewModel de settings de OctoPrint (para leer valores configurados)
        self.settingsViewModel = parameters[0];

        console.log("OctoFilament VM inicializado");

        // Observables Knockout para el icono del navbar
        self.iconClass = ko.observable("fa fa-question-circle"); // Icono por defecto
        self.iconColor = ko.observable("gray");                  // Color por defecto
        self.filamentStatus = ko.observable("...");              // Texto del estado

        // -------------------------------------------------------------------
        // onStartupComplete()
        // Se ejecuta cuando OctoPrint ha cargado todos los settings.
        // Aquí enlazamos los valores configurados con observables.
        // -------------------------------------------------------------------
        self.onStartupComplete = function() {
            console.log("OctoFilament: settings disponibles, inicializando observables");

            // Enlazar cada setting del plugin con su observable Knockout
            self.gpio_pin = self.settingsViewModel.settings.plugins.octofilament.gpio_pin;
            self.trigger_state = self.settingsViewModel.settings.plugins.octofilament.trigger_state;
            self.check_interval = self.settingsViewModel.settings.plugins.octofilament.check_interval;
            self.post_pause_gcode1 = self.settingsViewModel.settings.plugins.octofilament.post_pause_gcode1;
            self.post_pause_delay1 = self.settingsViewModel.settings.plugins.octofilament.post_pause_delay1;
            self.post_pause_gcode2 = self.settingsViewModel.settings.plugins.octofilament.post_pause_gcode2;
            self.post_pause_delay2 = self.settingsViewModel.settings.plugins.octofilament.post_pause_delay2;
            self.enable_debug_logs = self.settingsViewModel.settings.plugins.octofilament.enable_debug_logs;

            // Llamada inicial al estado del filamento
            self.updateStatus();

            // Refresco periódico según el intervalo configurado
            setInterval(self.updateStatus, self.check_interval() * 1000);
        };

        // -------------------------------------------------------------------
        // Cargar / descargar filamento
        // -------------------------------------------------------------------
        
        // Cargar filamento
        self.cargarFilamento = function() {
            const temp = self.settingsViewModel.settings.plugins.octofilament.LoadUnload_Temperature();
            OctoPrint.control.sendGcode(`M104 S${temp}`);
            OctoPrint.control.sendGcode("M83");
            OctoPrint.control.sendGcode("G1 E20 F300");
        };

        // Descargar filamento
        self.extraerFilamento = function() {
            const temp = self.settingsViewModel.settings.plugins.octofilament.LoadUnload_Temperature();
            OctoPrint.control.sendGcode(`M104 S${temp}`);
            OctoPrint.control.sendGcode("M83");
            OctoPrint.control.sendGcode("G1 E-20 F300");
        };

        // -------------------------------------------------------------------
        // updateStatus()
        // Consulta el estado del filamento al backend del plugin.
        // Llama a la API REST: /api/plugin/octofilament
        // -------------------------------------------------------------------
        self.updateStatus = function() {
            $.ajax({
                url: API_BASEURL + "plugin/octofilament",
                type: "GET",
                dataType: "json",

                // Si la API responde correctamente
                success: function(data) {
                    console.log("Estado de filamento recibido:", data.status);

                    // Actualizar observable
                    self.filamentStatus(data.status);

                    // Cambiar icono y color según estado
                    if (data.status === "absent") {
                        self.iconClass("fa fa-times");   // Cruz roja
                        self.iconColor("red");
                    } else if (data.status === "present") {
                        self.iconClass("fa fa-check");   // Check verde
                        self.iconColor("green");
                    } else {
                        self.iconClass("fa fa-question-circle"); // Estado desconocido
                        self.iconColor("gray");
                    }
                },

                // Si la API falla (por ejemplo, desconexión)
                error: function(xhr, status, error) {
                    console.error("Error consultando estado de filamento:", status, error);

                    self.filamentStatus("error");
                    self.iconClass("fa fa-exclamation-triangle"); // Icono de alerta
                    self.iconColor("orange");
                }
            });
        };
    }

    // -----------------------------------------------------------------------
    // Registro del ViewModel en OctoPrint
    // -----------------------------------------------------------------------
    // - "construct": función que crea el ViewModel
    // - "dependencies": otros ViewModels que deben cargarse antes
    // - "elements": elementos HTML donde se aplicará Knockout
    // -----------------------------------------------------------------------
    OCTOPRINT_VIEWMODELS.push({
        construct: OctoFilamentViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#navbar_plugin_octofilament"]
    });
});
