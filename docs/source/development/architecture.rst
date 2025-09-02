Architecture Guide
==================

This guide provides a comprehensive overview of AWS Services Reporter's architecture, design patterns, and implementation details for developers and contributors.

High-Level Architecture
-----------------------

AWS Services Reporter follows a modular, plugin-based architecture designed for extensibility, maintainability, and performance.

.. code-block:: text

   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │   CLI Interface │───▶│  Configuration  │───▶│  Core Engine    │
   │  (arg parsing)  │    │   Management    │    │   (main.py)     │
   └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                           │
   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │  Output Plugins │◀───│  Plugin System  │◀───│  Data Pipeline  │
   │ (csv,json,xml)  │    │   (discovery)   │    │  (processing)   │
   └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                           │
   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │  Cache System   │◀───│  Progress UI    │◀───│   AWS Client    │
   │ (intelligent)   │    │  (Rich/basic)   │    │ (SSM + RSS)     │
   └─────────────────┘    └─────────────────┘    └─────────────────┘

Core Modules
------------

**Core Package (aws_services_reporter/core/)**

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # config.py - Centralized configuration with validation
   @dataclass
   class Config:
       # AWS settings
       aws_profile: Optional[str] = None
       aws_region: str = "us-east-1"

       # Performance settings
       max_workers: int = 10
       max_retries: int = 3

       # Cache settings
       cache_enabled: bool = True
       cache_hours: int = 24
       cache_file: str = "reports/cache/aws_data_cache.json"

       # Output settings
       output_formats: List[str] = field(default_factory=lambda: ["csv"])
       output_dir: str = "reports"

       # Filtering settings (v1.5.0+)
       include_services: List[str] = field(default_factory=list)
       exclude_services: List[str] = field(default_factory=list)
       include_regions: List[str] = field(default_factory=list)
       exclude_regions: List[str] = field(default_factory=list)
       min_services: int = 0

Intelligent Caching
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # cache.py - TTL-based caching with corruption detection
   class AWSDataCache:
       def __init__(self, cache_file: str, ttl_hours: int = 24):
           """Initialize cache with TTL validation."""

       def is_valid(self) -> bool:
           """Check if cache is valid based on TTL and integrity."""

       def save(self, data: Dict[str, Any]) -> None:
           """Save data with metadata and timestamps."""

       def load(self) -> Optional[Dict[str, Any]]:
           """Load data with corruption detection."""

       def get_stats(self) -> Dict[str, Any]:
           """Generate comprehensive cache statistics."""

**Key Caching Features:**

- TTL-based invalidation with configurable duration
- Corruption detection using file size and JSON validation
- Metadata tracking (creation time, access count, data version)
- Statistics generation for cache effectiveness analysis
- Automatic cleanup and recovery from corrupted files

Progress Tracking
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # progress.py - Rich UI with graceful fallback
   class ProgressTracker:
       def __init__(self, use_rich: bool = True):
           """Initialize progress tracking with Rich library support."""

       def create_progress_bar(self, total: int, description: str):
           """Create progress bar with professional styling."""

       def display_completion_panel(self, stats: Dict[str, Any]):
           """Show completion summary with statistics."""

       def display_filter_summary(self, filter_stats: Dict[str, Any]):
           """Display filtering results and statistics."""

**AWS Client Package (aws_services_reporter/aws_client/)**

Session Management
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # session.py - Centralized AWS session handling
   def create_aws_session(profile: Optional[str] = None,
                         region: str = "us-east-1") -> boto3.Session:
       """Create AWS session with profile and region support."""

SSM Parameter Store Client
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ssm_client.py - Optimized SSM Parameter Store integration
   def get_all_regions_and_names(session: boto3.Session) -> Dict[str, Dict[str, Any]]:
       """Fetch all regions with metadata using batch operations."""

   def get_all_services_and_names(session: boto3.Session) -> Dict[str, str]:
       """Fetch service codes and display names efficiently."""

   def get_services_per_region_enhanced(
       session: boto3.Session,
       regions: Dict[str, Dict[str, Any]]
   ) -> Dict[str, List[str]]:
       """Get service availability per region with concurrency."""

**SSM Optimization Strategies:**

- Batch parameter retrieval (up to 10 parameters per API call)
- Concurrent region processing with ThreadPoolExecutor
- Exponential backoff for rate limiting
- Connection pooling for HTTP efficiency
- Smart parameter path construction to minimize API calls

RSS Feed Integration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # rss_client.py - Secure RSS parsing for launch dates
   def parse_rss_launch_dates(rss_url: str) -> Dict[str, Dict[str, Any]]:
       """Parse AWS RSS feed for region launch date information."""
       # Uses defusedxml for secure XML parsing
       # Implements requests for secure HTTP handling
       # Provides graceful fallback for network issues

**Security Features:**

- ``defusedxml`` for secure XML parsing (prevents XXE attacks)
- ``requests`` library for secure HTTP handling
- URL scheme validation (HTTPS/HTTP only)
- Input sanitization and validation
- Graceful fallback with security warnings

Data Processing Pipeline
------------------------

**Data Flow Architecture:**

.. code-block:: text

   AWS APIs ───┐
              ├──▶ Data Aggregation ──▶ Filtering ──▶ Plugin Processing ──▶ Output Files
   RSS Feed ───┘                         System          System

**Processing Stages:**

1. **Data Collection**:
   - SSM Parameter Store queries (regions, services, availability)
   - RSS feed parsing for launch dates
   - Data validation and sanitization

2. **Data Merging**:
   - Combine SSM and RSS data sources
   - Prioritize data sources (RSS > SSM > Unknown)
   - Generate comprehensive metadata

3. **Filtering Application** (v1.5.0+):
   - Service pattern matching with wildcards
   - Region filtering by code and name
   - Capacity-based filtering (minimum service count)
   - Filter validation and statistics

4. **Plugin Processing**:
   - Plugin discovery and registration
   - Format-specific data transformation
   - Dependency checking and graceful fallback
   - Concurrent plugin execution

Plugin System Architecture
--------------------------

**Plugin Interface Design:**

.. code-block:: python

   # plugins/base.py - Abstract base class defining plugin interface
   from abc import ABC, abstractmethod

   class BaseOutputPlugin(ABC):
       # Required class attributes
       name: str              # Unique plugin identifier
       description: str       # Human-readable description
       file_extension: str    # Output file extension
       requires_dependencies: List[str] = []  # Optional dependencies

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
           """Generate output in plugin-specific format."""

**Plugin Discovery System:**

.. code-block:: python

   # plugins/discovery.py - Automatic plugin discovery
   class PluginRegistry:
       def __init__(self):
           """Initialize plugin registry with automatic discovery."""

       def discover_plugins(self) -> None:
           """Automatically discover plugins in plugins directory."""

       def register_plugin(self, plugin_class: Type[BaseOutputPlugin]) -> None:
           """Register individual plugin with validation."""

       def get_available_plugins(self) -> Dict[str, BaseOutputPlugin]:
           """Get all available plugins with dependency checking."""

**Plugin Lifecycle:**

1. **Discovery**: Scan plugins directory for valid plugin classes
2. **Registration**: Validate plugin interface and register
3. **Dependency Check**: Verify optional dependencies on usage
4. **Instantiation**: Create plugin instance when needed
5. **Execution**: Call generate_output with full dataset
6. **Error Handling**: Graceful fallback if plugin fails

Performance Architecture
------------------------

**Concurrency Design:**

.. code-block:: python

   # Concurrent processing with ThreadPoolExecutor
   with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
       futures = []
       for region_code in regions:
           future = executor.submit(get_region_services, session, region_code)
           futures.append((region_code, future))

       # Process results as they complete
       for region_code, future in futures:
           try:
               services = future.result(timeout=30)
               region_services[region_code] = services
           except Exception as e:
               handle_region_error(region_code, e)

**Caching Strategy:**

.. code-block:: text

   Cache Decision Tree:

   Request ──▶ Cache Exists? ──No──▶ Fetch from AWS ──▶ Cache Data ──▶ Return
               │
               Yes
               │
               ▼
           Cache Valid? ──No──▶ Fetch from AWS ──▶ Update Cache ──▶ Return
               │
               Yes
               │
               ▼
           Return Cached Data

**Memory Management:**

- Streaming data processing to minimize memory usage
- Generator patterns for large datasets
- Efficient data structures (dict vs list optimization)
- Garbage collection awareness in long-running operations

Error Handling Architecture
---------------------------

**Error Hierarchy:**

.. code-block:: python

   class AWSServicesReporterError(Exception):
       """Base exception for all application errors."""

   class AWSIntegrationError(AWSServicesReporterError):
       """AWS API related errors."""

   class CacheError(AWSServicesReporterError):
       """Cache system errors."""

   class PluginError(AWSServicesReporterError):
       """Plugin system errors."""

   class ConfigurationError(AWSServicesReporterError):
       """Configuration validation errors."""

**Error Handling Patterns:**

1. **Graceful Degradation**: Continue operation with reduced functionality
2. **Retry Logic**: Exponential backoff for transient errors
3. **Fallback Mechanisms**: Alternative data sources or simplified output
4. **Error Context**: Preserve error context for debugging
5. **User-Friendly Messages**: Convert technical errors to user-actionable messages

Filtering System Architecture (v1.5.0+)
---------------------------------------

**Filter Application Pipeline:**

.. code-block:: text

   Original Data ──▶ Service Filters ──▶ Region Filters ──▶ Capacity Filters ──▶ Filtered Data
                      (include/exclude)     (include/exclude)      (min-services)

**Pattern Matching Engine:**

.. code-block:: python

   # utils/filters.py - Advanced filtering with wildcards
   def apply_service_filters(
       services: Dict[str, str],
       include_patterns: List[str],
       exclude_patterns: List[str]
   ) -> Tuple[Dict[str, str], Dict[str, Any]]:
       """Apply service filters with wildcard pattern matching."""

       filtered_services = {}
       stats = {"included": 0, "excluded": 0, "patterns_matched": {}}

       # Implementation using fnmatch for wildcard support
       for service_code, service_name in services.items():
           if should_include_service(service_code, include_patterns, exclude_patterns):
               filtered_services[service_code] = service_name
               stats["included"] += 1
           else:
               stats["excluded"] += 1

       return filtered_services, stats

**Filter Validation:**

- Pattern syntax validation before application
- Statistics generation for filter effectiveness
- User feedback about filter results
- Optimization for common filter patterns

Configuration Architecture
--------------------------

**Configuration Sources (Priority Order):**

1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration files (if implemented in future)
4. Default values (lowest priority)

**Configuration Validation:**

.. code-block:: python

   def validate_config(config: Config) -> List[str]:
       """Validate configuration and return list of issues."""
       issues = []

       if config.max_workers < 1 or config.max_workers > 50:
           issues.append("max_workers must be between 1 and 50")

       if config.cache_hours < 0:
           issues.append("cache_hours cannot be negative")

       # Additional validation logic
       return issues

Security Architecture
--------------------

**Security Principles:**

1. **Least Privilege**: Minimal required AWS permissions
2. **Input Validation**: All user inputs validated and sanitized
3. **Secure Dependencies**: Use secure libraries (defusedxml, requests)
4. **No Credential Storage**: Use AWS SDK credential chain
5. **Error Information**: No sensitive data in error messages

**AWS IAM Integration:**

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

**Security Scanning Integration:**

- Bandit security scanning in CI/CD
- Dependency vulnerability checking with Safety
- Regular security dependency updates
- Security-focused code review process

Testing Architecture
--------------------

**Test Categories and Coverage:**

.. code-block:: text

   Unit Tests ────────── Component Testing ── 95% coverage (critical modules)
   │                     │
   Integration Tests ──── AWS API Mocking ─── 85% coverage (API interactions)
   │                     │
   Performance Tests ──── Benchmarking ────── Key performance metrics
   │                     │
   Security Tests ────── Vulnerability ────── Zero high/medium issues

**Mocking Strategy:**

- ``moto`` library for AWS service mocking
- ``responses`` library for HTTP request mocking
- Custom fixtures for complex test scenarios
- Realistic test data that mirrors production

Future Architecture Considerations
----------------------------------

**Scalability Enhancements (Planned v2.0+):**

1. **Distributed Processing**: Multi-account and multi-region coordination
2. **Streaming Architecture**: Handle very large datasets efficiently
3. **Microservice Decomposition**: Split into focused service components
4. **Event-Driven Architecture**: React to AWS service changes in real-time

**Extension Points:**

1. **Plugin Architecture**: Already implemented for output formats
2. **Data Source Plugins**: Future support for additional data sources
3. **Processing Pipeline**: Configurable data transformation steps
4. **Storage Backends**: Pluggable storage for caching and persistence

**Performance Optimization Opportunities:**

1. **AsyncIO Integration**: Async/await for I/O-bound operations
2. **Caching Improvements**: Multi-level caching with Redis integration
3. **Data Compression**: Compressed data transfer and storage
4. **Connection Pooling**: Advanced HTTP connection management

Architecture Decision Records
-----------------------------

**ADR-001: Plugin-Based Architecture**
- **Decision**: Use plugin system for extensible output formats
- **Rationale**: Allows community contributions without core changes
- **Trade-offs**: Additional complexity vs. flexibility

**ADR-002: Intelligent Caching**
- **Decision**: TTL-based caching with corruption detection
- **Rationale**: 99% performance improvement with data integrity
- **Trade-offs**: Storage space vs. execution time

**ADR-003: Concurrent Processing**
- **Decision**: ThreadPoolExecutor for I/O-bound AWS API calls
- **Rationale**: Significant performance improvement for network operations
- **Trade-offs**: Complexity vs. performance (70% improvement achieved)

**ADR-004: Security-First Dependencies**
- **Decision**: Use defusedxml and requests for external data processing
- **Rationale**: Prevent security vulnerabilities in XML and HTTP handling
- **Trade-offs**: Additional dependencies vs. security assurance
