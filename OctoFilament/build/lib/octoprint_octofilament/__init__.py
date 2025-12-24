# -*- coding: utf-8 -*-
__plugin_name__ = "OctoFilament"
__plugin_identifier__ = "octofilament"
__plugin_version__ = "0.3.0"
__plugin_description__ = "Filament monitor with temp restore and multi-pause"
__plugin_pythoncompat__ = ">=3,<4"

from .octofilament import OctoFilamentPlugin
__plugin_implementation__ = OctoFilamentPlugin()
__plugin_hooks__ = {}


