Testing Guide
=============

AWS Services Reporter includes a comprehensive test suite designed to ensure reliability, performance, and compatibility. This guide covers testing strategies, running tests, and contributing test cases.

Test Suite Overview
-------------------

**Test Categories:**

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **AWS Integration Tests**: Mocked AWS API testing
- **Performance Tests**: Benchmarking and profiling
- **Security Tests**: Vulnerability scanning

**Coverage Goals:**

- Overall: 80%+ test coverage
- Critical modules: 95%+ coverage (cache, AWS clients)
- New features: 100% coverage required
- Bug fixes: Regression tests mandatory

Test Structure
--------------

.. code-block:: text

   tests/
   ├── test_cache.py              # Cache system comprehensive tests
   ├── test_aws_integration.py    # AWS API mocking with moto
   ├── test_configuration.py      # Config and CLI argument tests
   ├── test_output_formats.py     # Output generation tests
   ├── test_plugins.py            # Plugin system tests
   ├── test_filters.py            # Filtering logic tests
   ├── test_performance.py        # Performance benchmarks
   └── conftest.py                # Shared fixtures and utilities

Running Tests
-------------

**Basic Test Execution:**

.. code-block:: bash

   # Run all tests with coverage
   python -m pytest tests/ -v --cov=aws_services_reporter --cov-report=term-missing

   # Run specific test file
   python -m pytest tests/test_cache.py -v

   # Run with specific pattern
   python -m pytest tests/ -k "cache" -v

**Advanced Test Options:**

.. code-block:: bash

   # Run tests with detailed output
   python -m pytest tests/ -v -s --tb=long

   # Run only failed tests from last run
   python -m pytest tests/ --lf

   # Run tests in parallel (with pytest-xdist)
   python -m pytest tests/ -n 4

   # Generate HTML coverage report
   python -m pytest tests/ --cov=aws_services_reporter --cov-report=html

**Test Environment Variables:**

.. code-block:: bash

   # Skip AWS integration tests (useful for offline development)
   export SKIP_AWS_TESTS=1
   python -m pytest tests/

   # Enable performance benchmarks
   export RUN_PERFORMANCE_TESTS=1
   python -m pytest tests/test_performance.py

Unit Tests
----------

**Cache System Tests (test_cache.py):**

Tests the intelligent caching system with TTL validation, corruption detection, and statistics generation.

.. code-block:: python

   class TestCacheSystem:
       def test_cache_creation_and_initialization(self, tmp_path):
           """Test cache file creation with proper initialization."""

       def test_cache_ttl_validation(self, tmp_path):
           """Test TTL-based cache invalidation logic."""

       def test_cache_corruption_detection(self, tmp_path):
           """Test detection and handling of corrupted cache files."""

       def test_cache_statistics_generation(self, tmp_path):
           """Test generation of cache statistics and metadata."""

**Configuration Tests (test_configuration.py):**

Tests CLI argument parsing, configuration validation, and default value handling.

.. code-block:: python

   class TestConfiguration:
       def test_default_configuration_creation(self):
           """Test creation of configuration with default values."""

       def test_cli_argument_parsing(self):
           """Test parsing of various CLI argument combinations."""

       def test_configuration_validation(self):
           """Test validation of configuration parameters."""

**Output Format Tests (test_output_formats.py):**

Tests generation of CSV, JSON, Excel, and plugin formats with various data combinations.

.. code-block:: python

   class TestOutputFormats:
       def test_csv_output_generation(self, sample_data):
           """Test CSV format generation with complete dataset."""

       def test_json_output_with_metadata(self, sample_data):
           """Test JSON output including metadata and statistics."""

       def test_excel_output_multiple_sheets(self, sample_data):
           """Test Excel output with multiple formatted worksheets."""

Integration Tests
-----------------

**AWS Integration Tests (test_aws_integration.py):**

Uses moto library to mock AWS services for comprehensive integration testing.

.. code-block:: python

   @mock_ssm
   class TestAWSIntegration:
       def test_ssm_parameter_fetching(self):
           """Test SSM Parameter Store data retrieval."""
           # Setup mock SSM parameters
           client = boto3.client("ssm", region_name="us-east-1")
           client.put_parameter(
               Name="/aws/service/global-infrastructure/regions",
               Value="us-east-1,us-west-2",
               Type="StringList"
           )

           # Test actual integration
           # ...

**Plugin System Tests (test_plugins.py):**

Tests plugin discovery, registration, and execution with dependency management.

.. code-block:: python

   class TestPluginSystem:
       def test_plugin_discovery_and_registration(self):
           """Test automatic discovery of available plugins."""

       def test_plugin_execution_with_dependencies(self):
           """Test plugin execution with optional dependencies."""

       def test_plugin_error_handling(self):
           """Test graceful handling of plugin failures."""

Performance Tests
-----------------

**Performance Benchmarks (test_performance.py):**

Validates performance characteristics and identifies regressions.

.. code-block:: python

   class TestPerformance:
       def test_cache_performance_improvement(self, benchmark):
           """Benchmark cache vs non-cache execution times."""

       def test_concurrent_processing_scaling(self, benchmark):
           """Test performance scaling with different worker counts."""

       def test_memory_usage_limits(self):
           """Verify memory usage stays within acceptable limits."""

       def test_large_dataset_handling(self):
           """Test performance with maximum realistic dataset sizes."""

**Benchmark Results Tracking:**

.. code-block:: bash

   # Run performance benchmarks with reporting
   python -m pytest tests/test_performance.py --benchmark-only --benchmark-sort=mean

   # Generate performance comparison reports
   python -m pytest tests/test_performance.py --benchmark-compare=baseline

Test Fixtures and Utilities
----------------------------

**Shared Fixtures (conftest.py):**

.. code-block:: python

   @pytest.fixture
   def sample_regions():
       """Provide sample region data for testing."""
       return {
           "us-east-1": {
               "name": "US East (N. Virginia)",
               "launch_date": "2006-08-25",
               "launch_date_source": "RSS"
           },
           "eu-west-1": {
               "name": "Europe (Ireland)",
               "launch_date": "2007-12-10",
               "launch_date_source": "RSS"
           }
       }

   @pytest.fixture
   def sample_services():
       """Provide sample service data for testing."""
       return {
           "ec2": "Amazon Elastic Compute Cloud (EC2)",
           "s3": "Amazon Simple Storage Service (S3)",
           "lambda": "AWS Lambda"
       }

   @pytest.fixture
   def temp_output_dir(tmp_path):
       """Provide temporary directory for output testing."""
       output_dir = tmp_path / "test_output"
       output_dir.mkdir()
       return output_dir

**Test Utilities:**

.. code-block:: python

   def assert_valid_csv_output(file_path):
       """Assert that CSV output file is valid and well-formed."""

   def assert_valid_json_output(file_path):
       """Assert that JSON output is valid and contains required fields."""

   def mock_aws_ssm_responses():
       """Create realistic mock responses for SSM API calls."""

Mocking Strategies
------------------

**AWS Service Mocking:**

We use the ``moto`` library for AWS service mocking:

.. code-block:: python

   import boto3
   from moto import mock_ssm

   @mock_ssm
   def test_ssm_integration():
       # Create mock SSM client
       client = boto3.client("ssm", region_name="us-east-1")

       # Setup mock data
       client.put_parameter(
           Name="/aws/service/global-infrastructure/regions",
           Value="us-east-1,us-west-2",
           Type="StringList"
       )

       # Test real application logic with mocked AWS

**HTTP Request Mocking:**

For RSS feed and external HTTP requests:

.. code-block:: python

   import responses

   @responses.activate
   def test_rss_feed_parsing():
       # Mock HTTP response
       responses.add(
           responses.GET,
           "https://aws.amazon.com/new/feed/",
           body="<rss>...</rss>",
           status=200
       )

       # Test RSS parsing logic

Testing Best Practices
-----------------------

**Test Organization:**

1. **Group related tests** in classes
2. **Use descriptive test names** explaining what is tested
3. **Test both success and failure cases**
4. **Include edge cases** and boundary conditions
5. **Keep tests independent** and isolated

**Test Data:**

1. **Use fixtures** for reusable test data
2. **Create realistic sample data** that mirrors production
3. **Test with empty datasets** and edge cases
4. **Use temporary files** for output testing
5. **Clean up test artifacts** after execution

**Assertion Patterns:**

.. code-block:: python

   # Good: Specific assertions with clear error messages
   assert cache.is_valid(), "Cache should be valid after creation"
   assert len(regions) == 38, f"Expected 38 regions, got {len(regions)}"

   # Good: Multiple specific assertions vs single complex one
   assert result is not None
   assert result["status"] == "success"
   assert "regions" in result

   # Avoid: Generic assertions without context
   assert result  # Not descriptive enough

**Error Testing:**

.. code-block:: python

   def test_invalid_cache_file_handling(self, tmp_path):
       """Test graceful handling of invalid cache files."""
       # Create corrupted cache file
       cache_file = tmp_path / "corrupted.json"
       cache_file.write_text("invalid json content")

       # Test error handling
       with pytest.raises(CacheCorruptionError) as exc_info:
           cache = AWSDataCache(str(cache_file))
           cache.load()

       assert "corrupted" in str(exc_info.value).lower()

Continuous Integration Testing
------------------------------

**GitHub Actions Pipeline:**

Our CI/CD pipeline runs comprehensive testing:

.. code-block:: yaml

   # .github/workflows/test.yml (simplified)
   - name: Run Tests
     run: |
       python -m pytest tests/ -v \
         --cov=aws_services_reporter \
         --cov-report=xml \
         --cov-report=term-missing

   - name: Security Scan
     run: bandit -r aws_services_reporter/ --severity-level medium

   - name: Type Checking
     run: mypy aws_services_reporter/ main.py --ignore-missing-imports

**Test Matrix:**

Tests run across multiple Python versions and platforms:

- Python 3.8, 3.9, 3.10, 3.11
- Ubuntu, macOS, Windows
- With and without optional dependencies

Test Development Guidelines
---------------------------

**Writing New Tests:**

1. **Start with test cases** before implementing features (TDD)
2. **Test the interface** not implementation details
3. **Use realistic test data** that represents actual usage
4. **Include performance expectations** for critical paths
5. **Document complex test scenarios** with comments

**Test Maintenance:**

1. **Update tests** when changing functionality
2. **Remove obsolete tests** for deprecated features
3. **Refactor test code** to reduce duplication
4. **Monitor test execution time** and optimize slow tests
5. **Review test coverage** reports regularly

**Contributing Tests:**

1. **Include tests** with all feature contributions
2. **Add regression tests** for bug fixes
3. **Test edge cases** and error conditions
4. **Follow existing test patterns** and naming conventions
5. **Document test purpose** and expected behavior

Debugging Tests
---------------

**Debugging Failed Tests:**

.. code-block:: bash

   # Run specific failed test with detailed output
   python -m pytest tests/test_cache.py::TestCacheSystem::test_ttl_validation -vvv -s

   # Run with Python debugger
   python -m pytest tests/test_cache.py::test_name --pdb

   # Run with additional logging
   python -m pytest tests/test_cache.py --log-cli-level=DEBUG

**Test Debugging Utilities:**

.. code-block:: python

   import logging
   import pytest

   def test_with_debug_logging():
       """Test with detailed logging for debugging."""
       logging.getLogger().setLevel(logging.DEBUG)
       # Test implementation with debug information

**Common Test Issues:**

1. **Timing issues** in concurrent tests - use proper synchronization
2. **File system permissions** - use temporary directories
3. **Mock data inconsistencies** - validate mock data matches production
4. **Test isolation** - ensure tests don't affect each other
5. **Resource cleanup** - properly clean up files, connections, etc.

Performance Testing
-------------------

**Benchmark Testing:**

.. code-block:: bash

   # Install performance testing dependencies
   pip install pytest-benchmark

   # Run performance benchmarks
   python -m pytest tests/test_performance.py --benchmark-only

   # Save baseline for comparison
   python -m pytest tests/test_performance.py --benchmark-save=baseline

**Performance Assertions:**

.. code-block:: python

   def test_cache_performance(self, benchmark):
       """Benchmark cache vs fresh data retrieval performance."""

       def cached_execution():
           # Cached code path
           return get_cached_data()

       def fresh_execution():
           # Fresh data retrieval
           return get_fresh_data()

       # Benchmark and assert performance improvement
       cached_time = benchmark(cached_execution)
       fresh_time = benchmark(fresh_execution)

       # Cache should be at least 10x faster
       assert cached_time < fresh_time / 10

Test Reporting
--------------

**Coverage Reports:**

.. code-block:: bash

   # Generate comprehensive coverage report
   python -m pytest tests/ --cov=aws_services_reporter \
     --cov-report=html \
     --cov-report=term-missing \
     --cov-report=xml

**Test Result Analysis:**

.. code-block:: bash

   # Generate JUnit XML for CI integration
   python -m pytest tests/ --junit-xml=test-results.xml

   # Generate test timing reports
   python -m pytest tests/ --durations=10
