Advanced Filtering
==================

AWS Services Reporter provides powerful filtering capabilities to customize your reports and focus on specific services or regions. This guide covers all filtering options with practical examples.

Service Filtering
-----------------

Filter AWS services using wildcard patterns to include or exclude specific services from your reports.

**Include Services:**

.. code-block:: bash

   # Include specific services
   python main.py --include-services "ec2" "s3" "lambda"

   # Use wildcard patterns
   python main.py --include-services "ec2*" "s3*"

   # Include compute services
   python main.py --include-services "*compute*" "*ec2*" "*lambda*"

**Exclude Services:**

.. code-block:: bash

   # Exclude batch services
   python main.py --exclude-services "batch*"

   # Exclude government and china services
   python main.py --exclude-services "*gov*" "*cn*"

   # Exclude deprecated services
   python main.py --exclude-services "*deprecated*" "*legacy*"

Region Filtering
----------------

Filter AWS regions using patterns that match both region codes and region names.

**Include Regions:**

.. code-block:: bash

   # Include US regions only
   python main.py --include-regions "us-*"

   # Include specific regions
   python main.py --include-regions "us-east-1" "us-west-2" "eu-west-1"

   # Include by name patterns (case insensitive)
   python main.py --include-regions "*virginia*" "*oregon*" "*ireland*"

**Exclude Regions:**

.. code-block:: bash

   # Exclude government cloud regions
   python main.py --exclude-regions "*gov*"

   # Exclude China regions
   python main.py --exclude-regions "cn-*"

   # Exclude Asia Pacific regions
   python main.py --exclude-regions "ap-*"

Capacity-Based Filtering
------------------------

Filter regions based on the number of available services to focus on major regions or identify emerging regions.

**Minimum Services:**

.. code-block:: bash

   # Only major regions (typically 200+ services)
   python main.py --min-services 200

   # Well-established regions (100+ services)
   python main.py --min-services 100

   # Exclude very new regions (50+ services)
   python main.py --min-services 50

Pattern Matching Rules
----------------------

AWS Services Reporter uses Python's ``fnmatch`` module for pattern matching:

**Wildcard Characters:**

- ``*`` - Matches any number of characters
- ``?`` - Matches any single character
- ``[seq]`` - Matches any character in sequence
- ``[!seq]`` - Matches any character not in sequence

**Examples:**

.. code-block:: bash

   # Services starting with 'ec2'
   --include-services "ec2*"

   # Services ending with 'db'
   --include-services "*db"

   # Services containing 'compute'
   --include-services "*compute*"

   # Three-letter service codes
   --include-services "???"

   # Services starting with vowels
   --include-services "[aeiou]*"

Practical Filtering Examples
----------------------------

**Focus on Core AWS Services:**

.. code-block:: bash

   python main.py \
     --include-services "ec2*" "s3*" "lambda*" "rds*" "dynamodb*" "cloudformation*" \
     --format json excel

**Exclude Specialized Services:**

.. code-block:: bash

   python main.py \
     --exclude-services "*batch*" "*sagemaker*" "*iot*" "*gaming*" \
     --exclude-regions "*gov*" "cn-*"

**US-Only Analysis:**

.. code-block:: bash

   python main.py \
     --include-regions "us-*" \
     --exclude-regions "*gov*" \
     --min-services 100 \
     --format region-summary

**European Compliance Analysis:**

.. code-block:: bash

   python main.py \
     --include-regions "eu-*" \
     --include-services "*security*" "*compliance*" "*kms*" "*cloudtrail*" \
     --format json

**Compute Services Global Availability:**

.. code-block:: bash

   python main.py \
     --include-services "ec2*" "lambda*" "*compute*" "batch*" "fargate*" \
     --min-services 50 \
     --format excel

**Storage Services Analysis:**

.. code-block:: bash

   python main.py \
     --include-services "s3*" "*storage*" "efs*" "fsx*" "*backup*" \
     --exclude-regions "cn-*" \
     --format csv json

Filter Combination Logic
------------------------

**Multiple Filters Work Together:**

1. **Include filters** are applied first (if specified)
2. **Exclude filters** are applied to the included set
3. **Capacity filters** (min-services) are applied last

**Example Process:**

.. code-block:: bash

   python main.py \
     --include-regions "us-*" "eu-*" \    # Start with US and EU regions
     --exclude-regions "*gov*" \          # Remove government regions
     --min-services 100                   # Keep only regions with 100+ services

This results in major commercial US and EU regions only.

Filter Validation and Feedback
------------------------------

**Validation Messages:**

The tool provides detailed feedback about applied filters:

.. code-block:: text

   Filter Summary:
   ✓ Service filters: included 245 services, excluded 89 services
   ✓ Region filters: included 18 regions, excluded 8 regions
   ✓ Capacity filters: 16 regions meet minimum service count of 50

**Debug Filtering:**

Use debug logging to see exactly what's being filtered:

.. code-block:: bash

   python main.py \
     --include-services "ec2*" \
     --log-level DEBUG \
     --quiet

Performance Considerations
--------------------------

**Filtering Benefits:**

- **Faster execution**: Fewer regions/services to process
- **Smaller output**: Focused reports are easier to analyze
- **Reduced API calls**: Less data to fetch from AWS
- **Better caching**: Filtered results cache more effectively

**Optimal Filtering:**

.. code-block:: bash

   # Fast analysis of core services in major regions
   python main.py \
     --include-regions "us-*" "eu-west-*" \
     --include-services "ec2*" "s3*" "lambda*" "rds*" \
     --min-services 100 \
     --cache-hours 4

Common Filter Patterns
----------------------

**Development Environment:**

.. code-block:: bash

   python main.py --include-regions "us-east-1" "us-west-2" "eu-west-1"

**Production Analysis:**

.. code-block:: bash

   python main.py --exclude-regions "*gov*" "cn-*" --min-services 50

**Cost Optimization Study:**

.. code-block:: bash

   python main.py --include-services "*storage*" "*compute*" "*database*"

**Compliance Audit:**

.. code-block:: bash

   python main.py \
     --include-services "*security*" "*compliance*" "*audit*" "*logging*" \
     --include-regions "us-*" "eu-*"

**New Region Assessment:**

.. code-block:: bash

   python main.py --min-services 0 --max-services 100  # (if implemented)

Troubleshooting Filters
------------------------

**No Results After Filtering:**

1. Check filter patterns for typos
2. Verify wildcard syntax
3. Use ``--log-level DEBUG`` to see what's being filtered
4. Start with broader patterns and narrow down

**Unexpected Results:**

1. Remember that filters are case-sensitive for exact matches
2. Use ``--log-level INFO`` to see filter summary
3. Test filters individually before combining
4. Check the generated filter validation messages
