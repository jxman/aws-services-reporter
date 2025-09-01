AWS Services Reporter Documentation
====================================

AWS Services Reporter is a high-performance Python tool that generates comprehensive reports of AWS services availability across all regions using AWS Systems Manager (SSM) Parameter Store. It features intelligent caching (99% time savings), modular architecture, multiple output formats, and professional progress tracking.

.. image:: https://img.shields.io/badge/version-1.5.0-blue.svg
   :target: https://github.com/jxman/aws-services-reporter
   :alt: Version

.. image:: https://img.shields.io/badge/python-3.8%2B-blue.svg
   :target: https://python.org
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://github.com/jxman/aws-services-reporter/blob/main/LICENSE
   :alt: License

Features
--------

* **Intelligent Caching**: 99% performance improvement (90s → 5s) with TTL-based validation
* **Plugin System**: Extensible output formats with dynamic discovery
* **Advanced Filtering**: Service and region filtering with wildcard patterns
* **Multiple Output Formats**: CSV, JSON, Excel, XML, and custom plugins
* **RSS Integration**: Enhanced launch dates from official AWS documentation
* **Rich Progress Tracking**: Beautiful terminal UI with professional status panels
* **High Performance**: Concurrent processing with exponential backoff

Quick Start
-----------

.. code-block:: bash

   # Install dependencies
   pip install -r requirements.txt

   # Generate basic CSV report
   python main.py

   # Multiple formats with filtering
   python main.py --format json excel xml --include-services "ec2*" --exclude-regions "*gov*"

   # View available plugins and filters
   python main.py --plugin-help

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/installation
   user_guide/quick_start
   user_guide/configuration
   user_guide/filtering
   user_guide/output_formats

.. toctree::
   :maxdepth: 2
   :caption: Plugin Development

   plugins/overview
   plugins/creating_plugins
   plugins/built_in_plugins

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   api/core
   api/aws_client
   api/output
   api/plugins
   api/utils

.. toctree::
   :maxdepth: 1
   :caption: Development

   development/contributing
   development/testing
   development/architecture

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
