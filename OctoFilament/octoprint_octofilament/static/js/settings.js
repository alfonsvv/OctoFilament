// ---------------------------------------------------------------------------
// OctoFilament - settings.js
// ---------------------------------------------------------------------------
// Este archivo registra el ViewModel encargado de manejar la sección de
// configuración del plugin dentro de los ajustes de OctoPrint.
//
// A diferencia del ViewModel del navbar, este no realiza lógica activa.
// Su única función es enlazar la plantilla settings.jinja2 con el sistema
// de settings de OctoPrint mediante Knockout.js.
//
// OctoPrint cargará este ViewModel automáticamente cuando se abra la
// ventana de ajustes.
// ---------------------------------------------------------------------------

$(function() {

    // -----------------------------------------------------------------------
    // ViewModel de configuración del plugin
    // -----------------------------------------------------------------------
    // "parameters" contiene otros ViewModels de OctoPrint.
    // En este caso solo necesitamos "settingsViewModel", que permite acceder
    // a los valores configurados del plugin.
    // -----------------------------------------------------------------------
    function OctoFilamentSettingsViewModel(parameters) {
        var self = this;

        // ViewModel principal de settings de OctoPrint
        // Aquí se almacenan todos los valores configurables del plugin.
        self.settingsViewModel = parameters[0];
    }

    // -----------------------------------------------------------------------
    // Registro del ViewModel en el sistema de OctoPrint
    // -----------------------------------------------------------------------
    // - construct: función que crea el ViewModel
    // - dependencies: otros ViewModels que deben cargarse antes
    // - elements: IDs de los elementos HTML donde se aplicará Knockout
    //
    // "#settings_plugin_octofilament" corresponde al <div> principal
    // definido en settings.jinja2.
    // -----------------------------------------------------------------------
    OCTOPRINT_VIEWMODELS.push({
        construct: OctoFilamentSettingsViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_octofilament"]
    });
});
