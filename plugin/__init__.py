from __future__ import annotations

from .client import LspBasedpyrightPlugin, ViewEventListener
from .commands import LspBasedpyrightCreateConfigurationCommand, LspBasedpyrightUpdateViewStatusTextCommand

__all__ = (
    # ST: core
    "plugin_loaded",
    "plugin_unloaded",
    # ST: commands
    "LspBasedpyrightCreateConfigurationCommand",
    "LspBasedpyrightUpdateViewStatusTextCommand",
    # ...
    "LspBasedpyrightPlugin",
    "ViewEventListener",
)


def plugin_loaded() -> None:
    """Executed when this plugin is loaded."""
    LspBasedpyrightPlugin.setup()


def plugin_unloaded() -> None:
    """Executed when this plugin is unloaded."""
    LspBasedpyrightPlugin.wf_attrs.clear()
    LspBasedpyrightPlugin.cleanup()
