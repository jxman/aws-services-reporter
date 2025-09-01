Creating Custom Plugins
=======================

The AWS Services Reporter plugin system allows you to create custom output formats easily. This guide walks through creating your own plugin.

Plugin Architecture
-------------------

All plugins inherit from the ``BaseOutputPlugin`` abstract class and implement the required methods:

.. code-block:: python

    from aws_services_reporter.plugins.base import BaseOutputPlugin
    from aws_services_reporter.core.config import Config
    from typing import Any, Dict, List, Optional

    class MyCustomPlugin(BaseOutputPlugin):
        # Required class attributes
        name = "mycustom"
        description = "My custom output format"
        file_extension = "txt"
        requires_dependencies = []  # Optional dependencies

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
            # Your implementation here
            pass

Required Attributes
-------------------

name
    Unique identifier for your plugin (lowercase, no spaces)

description
    Human-readable description of what your plugin does

file_extension
    File extension for output files (without the dot)

requires_dependencies
    List of Python packages required by your plugin (optional)

Required Methods
----------------

generate_output()
    Main method that creates the output file. Returns True on success, False on failure.

Step-by-Step Example
--------------------

Let's create a simple text plugin that generates a human-readable summary:

1. **Create the plugin file**: ``aws_services_reporter/plugins/text_plugin.py``

.. code-block:: python

    from pathlib import Path
    from typing import Any, Dict, List, Optional

    from ..core.config import Config
    from .base import BaseOutputPlugin


    class TextOutputPlugin(BaseOutputPlugin):
        name = "text"
        description = "Generate human-readable text summary"
        file_extension = "txt"
        requires_dependencies = []

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
            try:
                if not quiet:
                    print("  📝 Creating text output...")

                output_path = self.get_output_path(
                    config, Path(config.regions_filename).stem
                )

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("AWS Services Availability Report\\n")
                    f.write("=" * 40 + "\\n\\n")

                    # Summary statistics
                    total_regions = len(regions)
                    all_services = set()
                    for services in region_services.values():
                        all_services.update(services)

                    f.write(f"Total Regions: {total_regions}\\n")
                    f.write(f"Total Services: {len(all_services)}\\n\\n")

                    # Region details
                    f.write("Regions:\\n")
                    f.write("-" * 20 + "\\n")
                    for region_code in sorted(regions.keys()):
                        region_info = regions[region_code]
                        service_count = len(region_services.get(region_code, []))
                        f.write(f"{region_code}: {region_info['name']} ({service_count} services)\\n")

                if not quiet:
                    file_size = output_path.stat().st_size
                    print(f"    ✓ Created text output ({file_size:,} bytes)")

                self.logger.info(f"Created text output: {output_path}")
                return True

            except Exception as e:
                if not quiet:
                    print(f"  ❌ Failed to create text output: {e}")
                self.logger.error(f"Failed to create text output: {e}")
                return False

2. **Register the plugin** (automatic discovery handles this)

The plugin system will automatically discover your plugin if it's in the ``plugins`` directory.

Advanced Features
-----------------

Dependency Management
~~~~~~~~~~~~~~~~~~~~~

If your plugin requires external libraries, specify them in ``requires_dependencies``:

.. code-block:: python

    class MyAdvancedPlugin(BaseOutputPlugin):
        name = "advanced"
        description = "Advanced output format with special features"
        file_extension = "special"
        requires_dependencies = ["pandas", "matplotlib"]

The plugin system will check for these dependencies and gracefully handle missing packages.

Using the Configuration
~~~~~~~~~~~~~~~~~~~~~~~

Access configuration options through the ``config`` parameter:

.. code-block:: python

    def generate_output(self, config, ...):
        # Access output directory
        output_dir = config.output_dir

        # Check for quiet mode
        if config.quiet:
            # Suppress output
            pass

        # Access filtering options
        if config.include_services:
            # Handle service filtering
            pass

Error Handling
~~~~~~~~~~~~~~

Always implement proper error handling:

.. code-block:: python

    def generate_output(self, config, ...):
        try:
            # Your implementation
            return True
        except Exception as e:
            self.logger.error(f"Plugin failed: {e}")
            if not quiet:
                print(f"  ❌ Plugin error: {e}")
            return False

Testing Your Plugin
-------------------

Create a test file for your plugin:

.. code-block:: python

    # tests/test_text_plugin.py
    import pytest
    from aws_services_reporter.plugins.text_plugin import TextOutputPlugin
    from aws_services_reporter.core.config import Config

    def test_text_plugin_creation():
        plugin = TextOutputPlugin()
        assert plugin.name == "text"
        assert plugin.file_extension == "txt"

    def test_text_plugin_generate(tmp_path):
        plugin = TextOutputPlugin()
        config = Config(output_dir=str(tmp_path))

        regions = {"us-east-1": {"name": "US East (N. Virginia)"}}
        region_services = {"us-east-1": ["ec2", "s3"]}

        result = plugin.generate_output(
            config, regions, region_services, quiet=True
        )

        assert result is True
        output_file = tmp_path / "text" / "regions.txt"
        assert output_file.exists()

Plugin Distribution
-------------------

To distribute your plugin:

1. Package it as a separate Python package
2. Use entry points to register it
3. Document installation and usage
4. Submit to PyPI for easy installation

Best Practices
--------------

* Keep plugins focused on a single output format
* Implement comprehensive error handling
* Use the logger for debugging information
* Respect the ``quiet`` parameter
* Validate your output files
* Write tests for your plugin
* Document any special requirements
