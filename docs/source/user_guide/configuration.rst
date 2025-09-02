Configuration Guide
===================

AWS Services Reporter provides extensive configuration options through command-line arguments. This guide covers all available settings and their use cases.

AWS Configuration
------------------

**AWS Profile:**

.. code-block:: bash

   python main.py --profile production
   python main.py --profile development

**AWS Region (for API calls):**

.. code-block:: bash

   python main.py --region us-west-2
   python main.py --region eu-central-1

**Note:** The region parameter only affects which AWS region is used for API calls. The tool always scans all available AWS regions.

Output Configuration
--------------------

**Output Directory:**

.. code-block:: bash

   python main.py --output-dir /custom/path/
   python main.py --output-dir ~/aws-reports/

**Custom Filenames:**

.. code-block:: bash

   python main.py --regions-file custom_regions.csv
   python main.py --matrix-file custom_matrix.csv

**Output Formats:**

.. code-block:: bash

   python main.py --format csv
   python main.py --format json excel xml
   python main.py --format region-summary  # Region summary only

Performance Configuration
-------------------------

**Concurrent Workers:**

.. code-block:: bash

   python main.py --max-workers 5    # Conservative (slower connections)
   python main.py --max-workers 15   # Aggressive (fast connections)
   python main.py --max-workers 10   # Default (balanced)

**Retry Configuration:**

.. code-block:: bash

   python main.py --max-retries 5    # More resilient
   python main.py --max-retries 1    # Fail fast

Cache Configuration
-------------------

**Cache Duration:**

.. code-block:: bash

   python main.py --cache-hours 1     # 1 hour cache
   python main.py --cache-hours 24    # Default (24 hours)
   python main.py --cache-hours 168   # 1 week cache

**Cache Location:**

.. code-block:: bash

   python main.py --cache-file /custom/cache.json

**Cache Management:**

.. code-block:: bash

   python main.py --cache-stats       # View cache information
   python main.py --clear-cache       # Delete cache and exit
   python main.py --no-cache          # Bypass cache completely

Filtering Configuration
-----------------------

**Service Filtering:**

.. code-block:: bash

   # Include specific services (wildcard patterns supported)
   python main.py --include-services "ec2*" "s3*" "lambda*"

   # Exclude specific services
   python main.py --exclude-services "batch*" "*gov*"

**Region Filtering:**

.. code-block:: bash

   # Include specific regions
   python main.py --include-regions "us-*" "eu-west-*"

   # Exclude specific regions
   python main.py --exclude-regions "*gov*" "cn-*"

**Capacity-Based Filtering:**

.. code-block:: bash

   # Only include regions with minimum service count
   python main.py --min-services 50
   python main.py --min-services 100

**Combined Filtering:**

.. code-block:: bash

   python main.py \
     --include-regions "us-*" \
     --exclude-regions "*gov*" \
     --min-services 30 \
     --include-services "compute*" "storage*"

Logging and Debugging
---------------------

**Log Levels:**

.. code-block:: bash

   python main.py --log-level DEBUG    # Detailed debugging
   python main.py --log-level INFO     # Default informational
   python main.py --log-level WARNING  # Warnings only
   python main.py --log-level ERROR    # Errors only

**Output Control:**

.. code-block:: bash

   python main.py --quiet             # Suppress progress output

Plugin Configuration
--------------------

**View Available Plugins:**

.. code-block:: bash

   python main.py --plugin-help

**Use Plugin Formats:**

.. code-block:: bash

   python main.py --format xml        # Use XML plugin
   python main.py --format csv json xml  # Multiple including plugins

Environment Variables
---------------------

You can also use environment variables for AWS configuration:

.. code-block:: bash

   export AWS_PROFILE=production
   export AWS_DEFAULT_REGION=us-west-2
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret

Configuration Examples
----------------------

**Development Environment:**

.. code-block:: bash

   python main.py \
     --profile dev \
     --cache-hours 1 \
     --format json \
     --log-level DEBUG \
     --max-workers 5

**Production Reports:**

.. code-block:: bash

   python main.py \
     --profile prod \
     --format csv json excel \
     --output-dir /prod/reports/ \
     --cache-hours 24 \
     --quiet \
     --max-workers 15

**Quick Analysis:**

.. code-block:: bash

   python main.py \
     --include-regions "us-*" \
     --min-services 50 \
     --format region-summary \
     --quiet

**Custom Filtering:**

.. code-block:: bash

   python main.py \
     --include-services "ec2*" "s3*" "lambda*" "rds*" \
     --exclude-regions "*gov*" "cn-*" \
     --format json excel \
     --cache-hours 4

IAM Permissions Required
------------------------

Your AWS credentials need the following minimum permissions:

.. code-block:: json

   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "ssm:GetParametersByPath",
                   "ssm:GetParameter"
               ],
               "Resource": [
                   "arn:aws:ssm:*:*:parameter/aws/service/global-infrastructure/*"
               ]
           }
       ]
   }

For detailed IAM analysis, see the ``AWS_IAM_LEAST_PRIVILEGE_ANALYSIS.md`` file in the project root.
