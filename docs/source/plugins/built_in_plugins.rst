Built-in Plugins
================

AWS Services Reporter comes with several built-in plugins that demonstrate the plugin architecture and provide additional output formats. This section documents all included plugins.

XML Plugin
----------

The XML plugin provides hierarchical XML output suitable for system integration and data exchange.

**Plugin Details:**

- **Name**: ``xml``
- **Description**: XML format with hierarchical structure
- **File Extension**: ``.xml``
- **Dependencies**: None (uses Python standard library)
- **Output Location**: ``reports/xml/regions_services.xml``

**Usage:**

.. code-block:: bash

   python main.py --format xml
   python main.py --format csv json xml  # Combined with other formats

**Features:**

- Hierarchical XML structure with proper nesting
- Complete region and service information
- XML declaration and encoding specification
- Metadata section with generation details
- Service availability grouped by region
- Service definitions with display names

**XML Structure:**

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8"?>
   <aws_services_report generated="2025-09-02T10:30:00Z" version="1.5.0">
     <metadata>
       <total_regions>38</total_regions>
       <total_services>396</total_services>
       <cache_used>true</cache_used>
       <generation_time_seconds>5.2</generation_time_seconds>
     </metadata>

     <regions>
       <region code="us-east-1" service_count="389">
         <name>US East (N. Virginia)</name>
         <launch_date source="RSS">2006-08-25</launch_date>
         <announcement_url>https://aws.amazon.com/about-aws/whats-new/2006/08/24/</announcement_url>
         <services>
           <service>ec2</service>
           <service>s3</service>
           <service>lambda</service>
           <!-- ... more services ... -->
         </services>
       </region>
       <!-- ... more regions ... -->
     </regions>

     <services>
       <service code="ec2">
         <name>Amazon Elastic Compute Cloud (EC2)</name>
         <availability_count>38</availability_count>
         <regions>
           <region>us-east-1</region>
           <region>us-west-2</region>
           <region>eu-west-1</region>
           <!-- ... more regions ... -->
         </regions>
       </service>
       <!-- ... more services ... -->
     </services>
   </aws_services_report>

**Use Cases:**

- Integration with enterprise XML-based systems
- Data exchange with SOAP web services
- Configuration management systems that consume XML
- Legacy system integration requiring XML format
- Structured data processing with XML parsers

**Performance:**

- Generation time: ~3-4 seconds (typical dataset)
- File size: ~300-400 KB (complete dataset)
- Memory usage: <10 MB during generation

Future Built-in Plugins
------------------------

The following plugins are planned for future releases:

YAML Plugin (Planned v2.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Features:**
- Human-readable YAML format
- Configuration file compatible structure
- Support for complex nested data
- Comments and documentation inline

**Use Cases:**
- Configuration management (Ansible, Kubernetes)
- Infrastructure as Code templates
- Human-readable data exchange
- Documentation with inline comments

Database Plugin (Planned v2.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Features:**
- Direct database insertion (PostgreSQL, MySQL)
- Table creation and schema management
- Incremental updates and change tracking
- Connection pooling and transaction management

**Use Cases:**
- Data warehouse integration
- Business intelligence systems
- Automated reporting pipelines
- Historical data analysis

Cloud Integration Plugin (Planned v2.1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Features:**
- S3 bucket upload with versioning
- SNS/SQS message publishing
- CloudWatch custom metrics
- Lambda function trigger integration

**Use Cases:**
- Automated cloud workflows
- Real-time monitoring and alerting
- Serverless data processing
- Multi-account data aggregation

Visualization Plugin (Planned v2.2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Features:**
- Interactive HTML dashboards
- Service availability heat maps
- Regional expansion timelines
- Chart.js or D3.js based visualizations

**Use Cases:**
- Executive dashboards and reports
- Service availability monitoring
- Regional expansion planning
- Visual data exploration

Plugin Development Examples
---------------------------

The built-in plugins serve as excellent examples for custom plugin development:

**Simple Plugin Pattern (XML Plugin):**

.. code-block:: python

   class XMLOutputPlugin(BaseOutputPlugin):
       name = "xml"
       description = "XML format with hierarchical structure"
       file_extension = "xml"
       requires_dependencies = []  # No external dependencies

       def generate_output(self, config, regions, region_services,
                          service_names=None, enhanced_services=None,
                          metadata=None, quiet=False):
           # Generate XML content
           xml_content = self._generate_xml(regions, region_services, service_names)

           # Write to file
           output_file = self._get_output_file(config)
           with open(output_file, 'w', encoding='utf-8') as f:
               f.write(xml_content)

           return True

**Key Implementation Patterns:**

1. **Clean separation** of data processing and file I/O
2. **Helper methods** for complex formatting logic
3. **Error handling** with try/catch and boolean return
4. **Consistent file naming** using base class utilities
5. **Respect for configuration** settings and quiet mode

Plugin Testing
---------------

Built-in plugins are thoroughly tested with:

**Unit Tests:**
- Output format validation
- Error handling scenarios
- Configuration option testing
- Performance benchmarking

**Integration Tests:**
- Full application workflow testing
- Filter combination validation
- Cache integration verification
- Multi-format generation testing

**Manual Testing:**
- Output file validation with real data
- Performance testing with large datasets
- Compatibility testing with different Python versions
- Error scenario testing (permissions, disk space)

Plugin Performance Comparison
-----------------------------

Relative performance of built-in formats:

+----------+------------------+-------------+----------------+
| Format   | Generation Time  | File Size   | Memory Usage   |
+==========+==================+=============+================+
| CSV      | ~2-3 seconds     | ~250 KB     | <5 MB          |
+----------+------------------+-------------+----------------+
| JSON     | ~3-4 seconds     | ~180 KB     | <8 MB          |
+----------+------------------+-------------+----------------+
| Excel    | ~5-7 seconds     | ~120 KB     | <15 MB         |
+----------+------------------+-------------+----------------+
| XML      | ~3-4 seconds     | ~350 KB     | <10 MB         |
+----------+------------------+-------------+----------------+

*Note: Times and sizes are approximate for complete dataset (38 regions, 396 services)*

Plugin Compatibility
---------------------

All built-in plugins are compatible with:

**Core Features:**
- Intelligent caching system
- Advanced filtering (services, regions, capacity)
- Progress tracking and Rich UI
- Configuration management
- Error handling and logging

**Python Versions:**
- Python 3.8+
- Tested on Python 3.8, 3.9, 3.10, 3.11
- Cross-platform compatibility (Windows, macOS, Linux)

**AWS Integration:**
- All AWS regions and services
- SSM Parameter Store data
- RSS feed integration for launch dates
- Graceful handling of AWS API limitations

Contributing Built-in Plugins
------------------------------

To contribute a new built-in plugin:

1. **Follow the plugin interface** defined in ``BaseOutputPlugin``
2. **Add comprehensive tests** for the plugin functionality
3. **Document the plugin** thoroughly with examples
4. **Ensure no external dependencies** or make them truly optional
5. **Test performance** with large datasets
6. **Follow code style** guidelines (black, isort, flake8)

**Contribution Process:**

1. Create plugin in ``aws_services_reporter/plugins/`` directory
2. Add unit tests in ``tests/`` directory
3. Update documentation in ``docs/source/plugins/``
4. Add plugin to CI/CD pipeline testing
5. Submit pull request with comprehensive description

Plugin Security Considerations
-------------------------------

Built-in plugins follow security best practices:

**File System Access:**
- Only write to configured output directories
- Validate file paths and extensions
- Handle permission errors gracefully
- No arbitrary file system access

**Data Handling:**
- Process only provided AWS data
- No external network requests (except core application)
- No credential or sensitive data logging
- Memory-efficient processing to prevent DoS

**Error Handling:**
- Graceful degradation on errors
- No sensitive information in error messages
- Proper exception handling and cleanup
- Return status indicating success/failure

Getting Support
---------------

For issues with built-in plugins:

1. **Check the troubleshooting section** in the main documentation
2. **Use debug logging** to identify specific issues:

   .. code-block:: bash

      python main.py --format xml --log-level DEBUG

3. **Verify dependencies** are installed correctly
4. **Test with minimal configuration** to isolate issues
5. **Review plugin-specific error messages** in output

For plugin development questions, see :doc:`creating_plugins` for detailed guidance.
