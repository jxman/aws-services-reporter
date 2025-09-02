Plugin System Overview
======================

The AWS Services Reporter plugin system provides a flexible architecture for extending output formats beyond the built-in CSV, JSON, and Excel options. This system allows developers to create custom output formats while maintaining compatibility with the core application.

Architecture
------------

The plugin system is built on a simple but powerful architecture:

1. **Base Plugin Class**: All plugins inherit from ``BaseOutputPlugin``
2. **Plugin Registry**: Automatic discovery and registration of available plugins
3. **Dynamic Loading**: Plugins are loaded on-demand with dependency checking
4. **Graceful Fallback**: Missing dependencies don't break the core application

Key Components
--------------

BaseOutputPlugin
    Abstract base class defining the plugin interface

PluginRegistry
    Manages plugin discovery, registration, and lifecycle

Plugin Discovery
    Automatic detection of plugins in the plugins directory

Dependency Management
    Optional dependency checking with graceful fallback

Plugin Interface
----------------

Every plugin must implement the following interface:

.. code-block:: python

   from aws_services_reporter.plugins.base import BaseOutputPlugin

   class MyPlugin(BaseOutputPlugin):
       # Required class attributes
       name = "myformat"
       description = "My custom output format"
       file_extension = "myext"
       requires_dependencies = ["optional-package"]  # Optional

       # Required method
       def generate_output(self, config, regions, region_services,
                          service_names=None, enhanced_services=None,
                          metadata=None, quiet=False):
           # Implementation here
           return True  # Success

Built-in Plugins
----------------

XML Plugin
~~~~~~~~~~

The XML plugin demonstrates the plugin architecture with a complete implementation:

- **Name**: ``xml``
- **Description**: "XML format with hierarchical structure"
- **Features**: Hierarchical XML output with metadata
- **Dependencies**: None (uses Python standard library)

Plugin Lifecycle
-----------------

1. **Discovery**: Plugins are discovered at application startup
2. **Registration**: Valid plugins are registered in the plugin registry
3. **Validation**: Dependencies are checked when plugins are used
4. **Execution**: Plugin ``generate_output`` method is called
5. **Error Handling**: Graceful fallback if plugin fails

Using Plugins
-------------

**List Available Plugins:**

.. code-block:: bash

   python main.py --plugin-help

**Use Plugin Formats:**

.. code-block:: bash

   python main.py --format xml
   python main.py --format csv json xml

**Plugin Output Location:**

Plugin outputs are saved in format-specific subdirectories under ``reports/``:

.. code-block:: text

   reports/
   ├── csv/
   ├── json/
   ├── excel/
   ├── xml/              # XML plugin output
   │   └── regions_services.xml
   └── cache/

Plugin Development Benefits
---------------------------

**For Developers:**

- Simple, well-defined interface
- Automatic integration with CLI and core functionality
- Built-in error handling and logging
- Access to full dataset and configuration
- No need to handle caching, filtering, or AWS integration

**For Users:**

- Seamless integration with existing workflow
- Consistent command-line interface
- Same filtering and configuration options
- Automatic dependency management
- No additional setup required

Plugin Development Workflow
---------------------------

1. **Create Plugin File**: Add new Python file in ``plugins/`` directory
2. **Implement Interface**: Inherit from ``BaseOutputPlugin``
3. **Test Plugin**: Use ``--plugin-help`` to verify registration
4. **Generate Output**: Test with ``--format yourplugin``
5. **Handle Dependencies**: Add optional dependencies as needed

Example Plugin Structure
------------------------

.. code-block:: python

   # aws_services_reporter/plugins/my_plugin.py

   from aws_services_reporter.plugins.base import BaseOutputPlugin
   from aws_services_reporter.core.config import Config
   import os

   class MyCustomPlugin(BaseOutputPlugin):
       name = "mycustom"
       description = "My custom output format"
       file_extension = "txt"
       requires_dependencies = []  # No special dependencies

       def generate_output(self, config: Config, regions, region_services,
                          service_names=None, enhanced_services=None,
                          metadata=None, quiet=False):
           try:
               # Create output directory
               output_dir = os.path.join(config.output_dir, self.name)
               os.makedirs(output_dir, exist_ok=True)

               # Generate output file
               output_file = os.path.join(
                   output_dir,
                   f"{config.regions_filename.replace('.csv', '')}.{self.file_extension}"
               )

               with open(output_file, 'w') as f:
                   # Your custom format logic here
                   f.write("Custom format content\\n")

               if not quiet:
                   print(f"Generated {self.description}: {output_file}")

               return True

           except Exception as e:
               print(f"Error generating {self.description}: {e}")
               return False

Advanced Plugin Features
------------------------

**Access to Full Dataset:**

Plugins receive complete access to:

- Region information with launch dates
- Service availability matrices
- Service display names
- Enhanced metadata from RSS feeds
- Configuration and filter settings

**Integration with Core Features:**

Plugins automatically benefit from:

- Intelligent caching system
- Advanced filtering capabilities
- Progress tracking and logging
- Error handling and retry logic
- AWS credential management

Plugin Registry API
--------------------

**Get Available Plugins:**

.. code-block:: python

   from aws_services_reporter.plugins.discovery import PluginRegistry

   registry = PluginRegistry()
   plugins = registry.get_available_plugins()

**Check Plugin Dependencies:**

.. code-block:: python

   plugin_instance = registry.get_plugin("xml")
   if plugin_instance and plugin_instance.check_dependencies():
       # Plugin is ready to use
       pass

Future Plugin Possibilities
---------------------------

The plugin architecture supports many potential extensions:

- **Database Output**: Direct insertion into PostgreSQL, MySQL
- **Cloud Integration**: Upload to S3, publish to SNS/SQS
- **Visualization**: Generate charts, graphs, or dashboards
- **Notification Formats**: Slack, email, or webhook payloads
- **Specialized Formats**: YAML, TOML, or custom binary formats
- **Analysis Plugins**: Statistical analysis or trend detection

Best Practices
--------------

**Plugin Development:**

1. Keep plugins focused on single output format
2. Handle errors gracefully and return boolean status
3. Respect the ``quiet`` parameter for output control
4. Use the provided configuration for file paths and settings
5. Document any optional dependencies clearly

**Dependency Management:**

1. Make dependencies truly optional when possible
2. Provide clear error messages for missing dependencies
3. Use try/except blocks for optional imports
4. Consider fallback behavior when dependencies are missing

**Testing:**

1. Test plugins with various filter combinations
2. Verify output with empty datasets
3. Test error handling with invalid configurations
4. Validate output format with representative data

Getting Help
------------

For plugin development assistance:

1. Review the built-in XML plugin implementation
2. Check the :doc:`creating_plugins` guide for detailed examples
3. Use ``--log-level DEBUG`` to troubleshoot plugin issues
4. Review the ``BaseOutputPlugin`` abstract class documentation
