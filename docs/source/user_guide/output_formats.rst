Output Formats
==============

AWS Services Reporter supports multiple output formats, each optimized for different use cases. This guide covers all available formats and their specific features.

Format Overview
---------------

+------------+----------------+---------------------+--------------------------------+
| Format     | File Extension | Use Case            | Features                       |
+============+================+=====================+================================+
| CSV        | .csv           | Data analysis       | Excel-compatible, lightweight  |
+------------+----------------+---------------------+--------------------------------+
| JSON       | .json          | API integration     | Rich metadata, structured data |
+------------+----------------+---------------------+--------------------------------+
| Excel      | .xlsx          | Business reports    | Multiple sheets, formatting    |
+------------+----------------+---------------------+--------------------------------+
| XML        | .xml           | System integration  | Hierarchical structure         |
+------------+----------------+---------------------+--------------------------------+

Output Directory Structure
--------------------------

All reports are organized in subdirectories under ``reports/``:

.. code-block:: text

   reports/
   ├── csv/                          # CSV format reports
   │   ├── regions_services.csv      # Main service matrix
   │   └── services_regions_matrix.csv # Transposed matrix
   ├── json/                         # JSON format with metadata
   │   └── regions_services.json     # Structured data with stats
   ├── excel/                        # Excel workbooks
   │   └── regions_services.xlsx     # Multi-sheet workbook
   ├── xml/                          # XML format (plugin)
   │   └── regions_services.xml      # Hierarchical XML structure
   └── cache/                        # Cache files
       └── aws_data_cache.json       # Cached AWS data

CSV Format
----------

**Features:**
- Lightweight and fast to generate
- Excel and spreadsheet application compatible
- Two complementary views of the data

**Files Generated:**

``regions_services.csv``
  Main report with regions as rows and services as columns.

``services_regions_matrix.csv``
  Transposed view with services as rows and regions as columns.

**Usage:**

.. code-block:: bash

   python main.py --format csv

**Sample CSV Structure:**

.. code-block:: text

   Region Code,Region Name,Launch Date,Data Source,Service Count,ec2,s3,lambda,...
   us-east-1,US East (N. Virginia),2006-08-25,RSS,389,✓,✓,✓,...
   eu-west-1,Europe (Ireland),2007-12-10,RSS,344,✓,✓,✓,...

JSON Format
-----------

**Features:**
- Rich metadata and statistics
- API-friendly structured format
- Launch date information with data sources
- Generation timestamps and cache info

**Usage:**

.. code-block:: bash

   python main.py --format json

**JSON Structure:**

.. code-block:: json

   {
     "metadata": {
       "generated_at": "2025-09-02T10:30:00Z",
       "version": "1.5.0",
       "total_regions": 38,
       "total_services": 396,
       "cache_used": true,
       "filters_applied": {
         "include_services": ["ec2*", "s3*"],
         "exclude_regions": ["*gov*"]
       }
     },
     "statistics": {
       "regions_with_launch_dates": 33,
       "data_sources": {
         "RSS": 33,
         "SSM": 0,
         "Unknown": 5
       },
       "service_coverage": {
         "min": 89,
         "max": 389,
         "average": 247.5
       }
     },
     "regions": {
       "us-east-1": {
         "name": "US East (N. Virginia)",
         "launch_date": "2006-08-25",
         "launch_date_source": "RSS",
         "announcement_url": "https://aws.amazon.com/...",
         "service_count": 389,
         "services": ["ec2", "s3", "lambda", ...]
       }
     },
     "services": {
       "ec2": "Amazon Elastic Compute Cloud (EC2)",
       "s3": "Amazon Simple Storage Service (S3)"
     }
   }

Excel Format
------------

**Features:**
- Professional multi-sheet workbooks
- Formatted tables with headers
- Region summary worksheet
- Service statistics
- Cell formatting and styling

**Usage:**

.. code-block:: bash

   python main.py --format excel

**Worksheets:**

1. **Service Matrix**: Complete service availability matrix
2. **Region Summary**: Regional statistics and launch dates
3. **Service List**: All services with display names
4. **Statistics**: Summary metrics and data sources

**Dependencies:**
Requires ``pandas`` and ``openpyxl`` packages (included in requirements.txt).

XML Format (Plugin)
-------------------

**Features:**
- Hierarchical XML structure
- System integration friendly
- Extensible schema
- Plugin-based implementation

**Usage:**

.. code-block:: bash

   python main.py --format xml

**XML Structure:**

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8"?>
   <aws_services_report generated="2025-09-02T10:30:00Z" version="1.5.0">
     <metadata>
       <total_regions>38</total_regions>
       <total_services>396</total_services>
       <cache_used>true</cache_used>
     </metadata>

     <regions>
       <region code="us-east-1" service_count="389">
         <name>US East (N. Virginia)</name>
         <launch_date source="RSS">2006-08-25</launch_date>
         <services>
           <service>ec2</service>
           <service>s3</service>
           <service>lambda</service>
         </services>
       </region>
     </regions>

     <services>
       <service code="ec2">
         <name>Amazon Elastic Compute Cloud (EC2)</name>
         <regions>
           <region>us-east-1</region>
           <region>eu-west-1</region>
         </regions>
       </service>
     </services>
   </aws_services_report>

Region Summary Format
---------------------

**Features:**
- Focused on regional information
- Launch dates and data sources
- Service counts per region
- Lightweight CSV format

**Usage:**

.. code-block:: bash

   python main.py --format region-summary

**Sample Output:**

.. code-block:: text

   Region Code,Region Name,Launch Date,Data Source,Service Count,Announcement URL
   us-east-1,US East (N. Virginia),2006-08-25,RSS,389,https://aws.amazon.com/...
   eu-west-1,Europe (Ireland),2007-12-10,RSS,344,https://aws.amazon.com/...

Multiple Formats
----------------

Generate multiple formats in a single run:

.. code-block:: bash

   # All formats
   python main.py --format csv json excel xml

   # Selected formats
   python main.py --format json excel

   # CSV variants
   python main.py --format csv region-summary

Format Selection Guidelines
---------------------------

**Choose CSV when:**
- Doing data analysis in Excel/spreadsheet tools
- Need lightweight, fast generation
- Working with large datasets
- Integrating with legacy systems

**Choose JSON when:**
- Building APIs or web applications
- Need rich metadata and statistics
- Working with modern development tools
- Require structured data processing

**Choose Excel when:**
- Creating business presentations
- Need professional formatting
- Working with non-technical stakeholders
- Want multiple data views in one file

**Choose XML when:**
- Integrating with enterprise systems
- Need hierarchical data structure
- Working with SOAP services or legacy XML systems
- Following XML-based standards

**Choose Region Summary when:**
- Focusing on regional analysis only
- Need quick regional overview
- Building regional expansion plans
- Monitoring new region launches

Format-Specific Options
-----------------------

**Cache Integration:**
All formats benefit from intelligent caching:

.. code-block:: bash

   python main.py --format json excel --cache-hours 4

**Filtering:**
All formats respect filter settings:

.. code-block:: bash

   python main.py \
     --format csv json \
     --include-regions "us-*" \
     --include-services "ec2*" "s3*"

**Custom Output Directory:**

.. code-block:: bash

   python main.py \
     --format excel xml \
     --output-dir ~/custom-reports/

Performance Characteristics
---------------------------

**Generation Speed (typical):**
- CSV: ~2-3 seconds
- JSON: ~3-4 seconds
- Excel: ~5-7 seconds (requires pandas processing)
- XML: ~3-4 seconds
- Region Summary: ~1-2 seconds

**File Sizes (typical full dataset):**
- CSV: ~200-300 KB total
- JSON: ~150-200 KB
- Excel: ~100-150 KB (compressed format)
- XML: ~300-400 KB
- Region Summary: ~5-10 KB

**Memory Usage:**
All formats use streaming generation to minimize memory usage, typically under 50MB even for complete datasets.

Troubleshooting Output Issues
-----------------------------

**Missing Files:**
Check the ``reports/`` subdirectories for your chosen format.

**Permission Errors:**
Ensure write permissions on the output directory:

.. code-block:: bash

   python main.py --output-dir ~/aws-reports/

**Excel Dependencies:**
Install required packages for Excel format:

.. code-block:: bash

   pip install pandas openpyxl

**Empty Files:**
Check AWS credentials and permissions. Use debug logging:

.. code-block:: bash

   python main.py --format json --log-level DEBUG
