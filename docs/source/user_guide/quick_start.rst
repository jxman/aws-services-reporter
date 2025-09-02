Quick Start Guide
=================

This guide will get you up and running with AWS Services Reporter in minutes.

Prerequisites
-------------

- Python 3.8 or higher
- AWS CLI configured with appropriate credentials
- Basic understanding of AWS services and regions

Installation
------------

1. **Clone or download the project**:

   .. code-block:: bash

      git clone <repository-url>
      cd aws-services-reporter

2. **Create a virtual environment**:

   .. code-block:: bash

      python3 -m venv .venv
      source .venv/bin/activate  # Linux/Mac
      # OR
      .venv\Scripts\activate     # Windows

3. **Install dependencies**:

   .. code-block:: bash

      pip install -r requirements.txt

4. **Verify AWS credentials**:

   .. code-block:: bash

      aws sts get-caller-identity

Basic Usage
-----------

Generate your first report with default settings:

.. code-block:: bash

   python main.py

This command will:

- Generate CSV reports in ``reports/csv/`` directory
- Cache data for 24 hours for faster subsequent runs
- Use default AWS profile and region settings
- Show progress with Rich UI components

Common Commands
---------------

**Multiple output formats:**

.. code-block:: bash

   python main.py --format csv json excel xml

**View available options:**

.. code-block:: bash

   python main.py --help
   python main.py --examples

**Check cache status:**

.. code-block:: bash

   python main.py --cache-stats

**Generate fresh data (bypass cache):**

.. code-block:: bash

   python main.py --no-cache

**Silent execution:**

.. code-block:: bash

   python main.py --quiet

Performance Tips
----------------

**First run optimization:**
The first run takes ~90 seconds to collect fresh data from AWS APIs. Subsequent runs use intelligent caching and complete in ~5 seconds (99% improvement).

**Concurrent processing:**
Increase workers for faster execution on high-bandwidth connections:

.. code-block:: bash

   python main.py --max-workers 20

**Cache management:**
Adjust cache duration based on your needs:

.. code-block:: bash

   python main.py --cache-hours 72  # 3-day cache

Output Locations
----------------

Reports are organized in subdirectories:

.. code-block:: text

   reports/
   ├── csv/                    # CSV format reports
   ├── json/                   # JSON format with metadata
   ├── excel/                  # Excel workbooks
   ├── xml/                    # XML format (plugin)
   └── cache/                  # Cached data

Understanding the Output
------------------------

**CSV Reports:**
- ``regions_services.csv``: Complete service availability matrix
- ``services_regions_matrix.csv``: Transposed view for analysis

**JSON Reports:**
- Rich metadata including statistics and data sources
- Launch date information where available
- Cache information and generation timestamps

**Excel Reports:**
- Multiple worksheets with formatted data
- Region summary with service counts
- Professional formatting for presentations

Next Steps
----------

- Learn about :doc:`filtering` to customize reports
- Explore :doc:`output_formats` for detailed format information
- See :doc:`configuration` for advanced customization
- Read :doc:`../plugins/creating_plugins` to create custom outputs
