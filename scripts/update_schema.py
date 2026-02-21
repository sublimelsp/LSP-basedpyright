#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, cast
from urllib.request import urlopen

PACKAGE_NAME = "LSP-basedpyright"

PROJECT_ROOT = Path(__file__).parents[1]
SCHEMA_ID = "sublime://basedpyright"
PYRIGHT_CONFIGURATION_SCHEMA_URL = "https://raw.githubusercontent.com/DetachHead/basedpyright/main/packages/vscode-pyright/schemas/pyrightconfig.schema.json"
VSCODE_EXTENSION_PACKAGE_JSON_URL = (
    "https://raw.githubusercontent.com/DetachHead/basedpyright/main/packages/vscode-pyright/package.json"
)
SUBLIME_PACKAGE_JSON_PATH = PROJECT_ROOT / "sublime-package.json"
UPDATE_SCHEMA_SETTINGS_PATH = PROJECT_ROOT / "scripts" / "update_schema_settings.json"

JsonDict = Dict[str, Any]


def main() -> None:
    pyrightconfig_schema, extension_configuration, sublime_package_schema = read_schemas()
    before = serialize_json_object(sublime_package_schema)
    update_schema(sublime_package_schema, pyrightconfig_schema, extension_configuration)
    after = serialize_json_object(sublime_package_schema)
    if before != after:
        SUBLIME_PACKAGE_JSON_PATH.write_text(f"{after}\n", encoding="utf-8")
        print("sublime-package.json schema updated.")
    else:
        print("No updates done to sublime-package.json.")


def read_schemas() -> tuple[JsonDict, JsonDict, JsonDict]:
    with urlopen(PYRIGHT_CONFIGURATION_SCHEMA_URL) as response:
        pyrightconfig_schema: JsonDict = json.load(response)
    create_all_property_definitions(pyrightconfig_schema)
    with urlopen(VSCODE_EXTENSION_PACKAGE_JSON_URL) as response:
        extension_configuration: JsonDict = json.load(response)["contributes"]["configuration"]["properties"]
    sublime_package_schema: JsonDict = json.loads(SUBLIME_PACKAGE_JSON_PATH.read_bytes())
    return (pyrightconfig_schema, extension_configuration, sublime_package_schema)


def serialize_json_object(obj: JsonDict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True)


def update_schema(
    sublime_package_schema: JsonDict, pyrightconfig_schema: JsonDict, extension_configuration: JsonDict
) -> None:
    pyrightconfig_contribution, lsp_pyright_contribution = get_sublime_package_contributions(sublime_package_schema)
    # Update to latest pyrightconfig schema and add ID.
    pyrightconfig_contribution["schema"] = pyrightconfig_schema
    pyrightconfig_contribution["schema"]["$id"] = SCHEMA_ID
    # Update LSP settings schema to upstream extension configuration schema.
    # Merge custom properties
    update_schema_settings: JsonDict = json.loads(UPDATE_SCHEMA_SETTINGS_PATH.read_bytes())
    cleanup_vscode_schema(extension_configuration)
    lsp_settings: JsonDict = {**extension_configuration, **update_schema_settings["merge"]}
    # Update LSP settings to reference definitions from the pyrightconfig schema.
    pyrightconfig_definitions: JsonDict = pyrightconfig_contribution["schema"]["definitions"]
    for setting_key, setting_value in lsp_settings.items():
        # get last dotted component.
        last_component_key = setting_key.rpartition(".")[2]
        if last_component_key in pyrightconfig_definitions:
            update_property_ref(last_component_key, setting_value)
        if setting_key == "basedpyright.analysis.diagnosticSeverityOverrides":
            overrides_properties: JsonDict = setting_value["properties"]
            for override_key, override_value in overrides_properties.items():
                if override_key in pyrightconfig_definitions:
                    update_property_ref(override_key, override_value)
    # fmt: off
    lsp_pyright_contribution["schema"]["definitions"]["PluginConfig"]["properties"]["settings"]["properties"] = lsp_settings  # noqa: E501
    # fmt: on


def get_sublime_package_contributions(sublime_package_schema: JsonDict) -> tuple[JsonDict, JsonDict]:
    settings = sublime_package_schema["contributions"]["settings"]
    try:
        return (
            next(c for c in settings if "/pyrightconfig.json" in c["file_patterns"]),
            next(c for c in settings if f"/{PACKAGE_NAME}.sublime-settings" in c["file_patterns"]),
        )
    except StopIteration:
        raise Exception("Expected contributions not found in sublime-package.json!")


def create_all_property_definitions(schema_json: JsonDict) -> None:
    """Modify schema so that there exists an entry in "definitions" for every of "properties"."""
    for key, definition in schema_json["properties"].items():
        if "$ref" in definition:
            continue
        schema_json["definitions"][key] = definition.copy()
        update_property_ref(key, definition, relative=True)


def update_property_ref(property_key: str, property_schema: JsonDict, *, relative: bool = False) -> None:
    property_schema.clear()
    property_schema["$ref"] = f"{'' if relative else SCHEMA_ID}#/definitions/{property_key}"


def cleanup_vscode_schema(schema: JsonDict) -> None:
    """Modify schema to remove unwanted properties (like VSCode-specific ones)."""
    for key in list(schema.keys()):
        if key == "scope":
            del schema[key]
        elif isinstance(schema[key], dict):
            cleanup_vscode_schema(cast(JsonDict, schema[key]))


if __name__ == "__main__":
    main()
