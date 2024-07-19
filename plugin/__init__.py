from __future__ import annotations

from .client import LspBasedpyrightPlugin
from .commands import LspBasedpyrightCreateConfigurationCommand

__all__ = (
    # ST: core
    "plugin_loaded",
    "plugin_unloaded",
    # ST: commands
    "LspBasedpyrightCreateConfigurationCommand",
    # ...
    "LspBasedpyrightPlugin",
)


def plugin_loaded() -> None:
    """Executed when this plugin is loaded."""
    LspBasedpyrightPlugin.setup()


def plugin_unloaded() -> None:
    """Executed when this plugin is unloaded."""
    LspBasedpyrightPlugin.window_attrs.clear()
    LspBasedpyrightPlugin.cleanup()
