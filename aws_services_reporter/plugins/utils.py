"""Plugin utility functions for CLI and main application integration."""

import logging
from typing import List

from .base import plugin_registry
from .discovery import auto_discover_and_load


def get_available_formats() -> List[str]:
    """Get list of all available output formats including plugins.

    Returns:
        List of format names (built-in + plugins)
    """
    # Built-in formats
    builtin_formats = [
        "csv",
        "json",
        "excel",
        "region-summary",
        "service-summary",
    ]

    # Auto-discover plugins if not already done
    auto_discover_and_load()

    # Get plugin formats
    plugin_formats = list(plugin_registry.list_plugins().keys())

    # Combine and return
    return builtin_formats + plugin_formats


def is_plugin_format(format_name: str) -> bool:
    """Check if a format is handled by a plugin.

    Args:
        format_name: Name of the format to check

    Returns:
        True if format is handled by a plugin, False otherwise
    """
    return format_name.lower() in plugin_registry.list_plugins()


def get_plugin_info() -> dict:
    """Get information about all registered plugins.

    Returns:
        Dictionary with plugin information
    """
    plugins_info = {}

    for name, plugin_class in plugin_registry.list_plugins().items():
        plugins_info[name] = {
            "name": plugin_class.name,
            "description": plugin_class.description,
            "file_extension": plugin_class.file_extension,
            "requires_dependencies": plugin_class.requires_dependencies,
            "available": plugin_class().check_dependencies(),
        }

    return plugins_info


def initialize_plugins(quiet: bool = False):
    """Initialize the plugin system.

    Args:
        quiet: Suppress output if True
    """
    logger = logging.getLogger(__name__)

    if not quiet:
        print("🔌 Initializing plugin system...")

    # Discover and load plugins
    auto_discover_and_load()

    # Report what was found
    plugins = plugin_registry.list_plugins()
    if not quiet:
        if plugins:
            print(f"   ✓ Loaded {len(plugins)} plugin(s): {', '.join(plugins.keys())}")
        else:
            print("   ℹ No plugins found")

    logger.info(f"Plugin system initialized with {len(plugins)} plugins")


def show_plugin_help():
    """Show detailed help about available plugins."""
    plugins_info = get_plugin_info()

    if not plugins_info:
        print("No plugins available.")
        return

    print("\n🔌 Available Plugin Formats:")
    print("=" * 50)

    for name, info in plugins_info.items():
        status = "✅ Available" if info["available"] else "❌ Missing dependencies"

        print(f"\n{name.upper()}:")
        print(f"  Description: {info['description']}")
        print(f"  File Extension: .{info['file_extension']}")
        print(f"  Status: {status}")

        if info["requires_dependencies"]:
            print(f"  Dependencies: {', '.join(info['requires_dependencies'])}")

        print(f"  Usage: python main.py --format {name}")


def list_plugin_formats() -> List[str]:
    """Get list of only plugin format names.

    Returns:
        List of plugin format names
    """
    return list(plugin_registry.list_plugins().keys())
