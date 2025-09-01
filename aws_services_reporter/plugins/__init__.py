"""Plugin system for AWS Services Reporter.

Provides extensible output format plugins with discovery and registration.
"""

from .base import BaseOutputPlugin, PluginRegistry
from .discovery import discover_plugins, load_plugin

__all__ = [
    "BaseOutputPlugin",
    "PluginRegistry",
    "discover_plugins",
    "load_plugin",
]
