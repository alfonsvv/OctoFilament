# -*- coding: utf-8 -*-
from setuptools import setup

plugin_identifier = "octofilament"
plugin_package = "octoprint_octofilament"
plugin_name = "octoprint-octofilament"
plugin_version = "0.3.0"
plugin_description = "Filament monitor with temp restore and multi-pause"
plugin_author = "Alfonso"
plugin_license = "AGPLv3"
plugin_url = "https://github.com/alfonsvv/OctoFilament"

setup(
    name=plugin_name,
    version=plugin_version,
    description=plugin_description,
    author=plugin_author,
    license=plugin_license,
    url=plugin_url,
    packages=[plugin_package],
    include_package_data=True,
    package_data={
        plugin_package: [
            "static/js/*.js",
            "static/css/*.css",
            "templates/*.jinja2"
        ]
    },
    install_requires=[],
    entry_points={
        "octoprint.plugin": [
            "octofilament = octoprint_octofilament"
        ]
    },
)
