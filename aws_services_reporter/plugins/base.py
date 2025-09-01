"""Base plugin interface and registry for AWS Services Reporter."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from ..core.config import Config


class BaseOutputPlugin(ABC):
    """Abstract base class for output format plugins.

    All output plugins must inherit from this class and implement the
    required methods to generate their specific output format.
    """

    # Plugin metadata - must be defined by subclasses
    name: str = ""
    description: str = ""
    file_extension: str = ""
    requires_dependencies: List[str] = []

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the plugin.

        Args:
            logger: Optional logger instance for plugin operations
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def generate_output(
        self,
        config: Config,
        regions: Dict[str, Dict[str, Any]],
        region_services: Dict[str, List[str]],
        service_names: Optional[Dict[str, str]] = None,
        enhanced_services: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        quiet: bool = False,
    ) -> bool:
        """Generate output in the plugin's format.

        Args:
            config: Configuration object containing output settings
            regions: Dictionary mapping region codes to region details
            region_services: Dictionary mapping region codes to service lists
            service_names: Dictionary mapping service codes to display names
            enhanced_services: Dictionary with enhanced service metadata per region
            metadata: Optional metadata about the data fetch operation
            quiet: Suppress progress output if True

        Returns:
            True if output was successfully generated, False otherwise

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement generate_output")

    def check_dependencies(self) -> bool:
        """Check if required dependencies are available.

        Returns:
            True if all required dependencies are available, False otherwise
        """
        if not self.requires_dependencies:
            return True

        try:
            for dependency in self.requires_dependencies:
                __import__(dependency)
            return True
        except ImportError as e:
            self.logger.warning(f"Plugin {self.name} missing dependency: {e}")
            return False

    def get_output_path(self, config: Config, filename: str) -> Path:
        """Get the output path for this plugin's files.

        Args:
            config: Configuration object
            filename: Base filename without extension

        Returns:
            Path object for the output file
        """
        plugin_dir = Path(config.output_dir) / self.name.lower()
        plugin_dir.mkdir(parents=True, exist_ok=True)

        output_filename = f"{filename}.{self.file_extension}"
        return plugin_dir / output_filename

    @classmethod
    def validate_plugin(cls) -> bool:
        """Validate that the plugin class has required attributes.

        Returns:
            True if plugin is valid, False otherwise
        """
        required_attrs = ["name", "description", "file_extension"]
        for attr in required_attrs:
            if not getattr(cls, attr, None):
                return False
        return True


class PluginRegistry:
    """Registry for managing output format plugins."""

    def __init__(self):
        """Initialize the plugin registry."""
        self.plugins: Dict[str, Type[BaseOutputPlugin]] = {}
        self.logger = logging.getLogger(__name__)

    def register(self, plugin_class: Type[BaseOutputPlugin]) -> bool:
        """Register a plugin class.

        Args:
            plugin_class: Plugin class to register

        Returns:
            True if plugin was registered successfully, False otherwise
        """
        if not plugin_class.validate_plugin():
            self.logger.error(
                f"Invalid plugin {plugin_class.__name__}: "
                "missing required attributes"
            )
            return False

        plugin_name = plugin_class.name.lower()
        if plugin_name in self.plugins:
            self.logger.warning(f"Plugin {plugin_name} already registered, overwriting")

        self.plugins[plugin_name] = plugin_class
        self.logger.info(f"Registered plugin: {plugin_name}")
        return True

    def get_plugin(self, name: str) -> Optional[Type[BaseOutputPlugin]]:
        """Get a plugin class by name.

        Args:
            name: Plugin name (case insensitive)

        Returns:
            Plugin class if found, None otherwise
        """
        return self.plugins.get(name.lower())

    def list_plugins(self) -> Dict[str, Type[BaseOutputPlugin]]:
        """Get all registered plugins.

        Returns:
            Dictionary mapping plugin names to plugin classes
        """
        return self.plugins.copy()

    def create_plugin(self, name: str) -> Optional[BaseOutputPlugin]:
        """Create an instance of a plugin.

        Args:
            name: Plugin name (case insensitive)

        Returns:
            Plugin instance if found and dependencies available, None otherwise
        """
        plugin_class = self.get_plugin(name)
        if not plugin_class:
            self.logger.error(f"Plugin not found: {name}")
            return None

        plugin = plugin_class()
        if not plugin.check_dependencies():
            self.logger.error(
                f"Plugin {name} dependencies not available: "
                f"{plugin.requires_dependencies}"
            )
            return None

        return plugin


# Global plugin registry instance
plugin_registry = PluginRegistry()
