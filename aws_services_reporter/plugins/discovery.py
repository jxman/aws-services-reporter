"""Plugin discovery and loading system."""

import importlib
import logging
import pkgutil
from pathlib import Path
from typing import List, Optional, Type

from .base import BaseOutputPlugin, plugin_registry


def discover_plugins(plugin_paths: Optional[List[Path]] = None) -> List[str]:
    """Discover available plugins in specified paths.

    Args:
        plugin_paths: List of paths to search for plugins.
                     If None, searches built-in plugin locations.

    Returns:
        List of discovered plugin names
    """
    logger = logging.getLogger(__name__)
    discovered = []

    if plugin_paths is None:
        # Default to built-in plugins
        plugin_paths = [Path(__file__).parent]

    for plugin_path in plugin_paths:
        if not plugin_path.exists():
            logger.debug(f"Plugin path does not exist: {plugin_path}")
            continue

        try:
            # Find all Python modules in the plugin path
            for finder, name, ispkg in pkgutil.iter_modules([str(plugin_path)]):
                if name.startswith("_") or name in ["base", "discovery"]:
                    continue  # Skip private modules and core files

                try:
                    plugin_module = load_plugin_module(name, plugin_path)
                    if plugin_module:
                        discovered.append(name)
                        logger.debug(f"Discovered plugin module: {name}")
                except Exception as e:
                    logger.warning(f"Failed to load plugin {name}: {e}")

        except Exception as e:
            logger.error(f"Error discovering plugins in {plugin_path}: {e}")

    logger.info(f"Discovered {len(discovered)} plugin modules")
    return discovered


def load_plugin_module(module_name: str, plugin_path: Path):
    """Load a plugin module and register any plugins found.

    Args:
        module_name: Name of the module to load
        plugin_path: Path where the module is located

    Returns:
        The loaded module if successful, None otherwise
    """
    logger = logging.getLogger(__name__)

    try:
        # Import the module using full package name
        full_module_name = f"aws_services_reporter.plugins.{module_name}"
        spec = importlib.util.spec_from_file_location(
            full_module_name, plugin_path / f"{module_name}.py"
        )
        if not spec or not spec.loader:
            logger.error(f"Could not load spec for {module_name}")
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Look for plugin classes in the module
        plugins_found = 0
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseOutputPlugin)
                and attr != BaseOutputPlugin
            ):

                # Register the plugin
                if plugin_registry.register(attr):
                    plugins_found += 1
                    logger.info(f"Loaded plugin: {attr.name}")

        if plugins_found == 0:
            logger.warning(f"No valid plugins found in module {module_name}")

        return module

    except Exception as e:
        logger.error(f"Error loading plugin module {module_name}: {e}")
        return None


def load_plugin(plugin_name: str) -> Optional[BaseOutputPlugin]:
    """Load and create an instance of a specific plugin.

    Args:
        plugin_name: Name of the plugin to load

    Returns:
        Plugin instance if found and loadable, None otherwise
    """
    return plugin_registry.create_plugin(plugin_name)


def auto_discover_and_load():
    """Automatically discover and load all available plugins."""
    logger = logging.getLogger(__name__)
    logger.info("Starting automatic plugin discovery")

    discovered = discover_plugins()
    logger.info(f"Plugin discovery complete. Found {len(discovered)} modules")

    # List registered plugins
    registered = plugin_registry.list_plugins()
    logger.info(f"Registered plugins: {list(registered.keys())}")


# Import utility for lazy loading
def import_optional(module_name: str):
    """Import a module if available, return None if not found.

    Args:
        module_name: Name of the module to import

    Returns:
        Imported module if available, None otherwise
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None
