"""Command-line interface utilities for AWS Services Reporter.

Handles argument parsing, help text generation, and CLI user interactions.
"""

import argparse
from typing import List


def parse_arguments() -> argparse.Namespace:
    """Parse and validate command line arguments.

    Returns:
        Namespace object containing parsed command line arguments

    Raises:
        SystemExit: If invalid arguments are provided or help is requested
    """
    parser = argparse.ArgumentParser(
        description="Generate comprehensive AWS services by region reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Basic run with defaults
  python main.py --output-dir ./reports            # Custom output directory
  python main.py --max-workers 15 --log-level DEBUG  # Performance tuning
  python main.py --profile production --region us-west-2  # AWS configuration
        """,
    )

    # Output configuration
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Output directory for generated files (default: reports)",
    )
    parser.add_argument(
        "--regions-file",
        default="regions_services.csv",
        help="Output filename for regions-services CSV (default: regions_services.csv)",
    )
    parser.add_argument(
        "--matrix-file",
        default="services_regions_matrix.csv",
        help="Output filename for services-regions matrix CSV (default: services_regions_matrix.csv)",
    )

    # Output formats
    valid_formats = ["csv", "json", "excel", "region-summary", "service-summary"]
    parser.add_argument(
        "--format",
        nargs="+",
        choices=valid_formats,
        default=["csv"],
        help=f"Output formats to generate: {', '.join(valid_formats)} (default: csv)",
    )

    # AWS configuration
    parser.add_argument(
        "--profile", help="AWS profile to use (default: default profile)"
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region for API calls (default: us-east-1)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts for failed API calls (default: 3)",
    )

    # Performance settings
    parser.add_argument(
        "--max-workers",
        type=int,
        default=10,
        help="Number of concurrent API calls (default: 10)",
    )

    # Caching system
    parser.add_argument(
        "--no-cache", action="store_true", help="Disable caching and fetch fresh data"
    )
    parser.add_argument(
        "--no-enhanced-metadata",
        action="store_true",
        help="Disable enhanced metadata fetching (launch dates, categories, etc.) for faster execution",
    )
    parser.add_argument(
        "--cache-hours",
        type=int,
        default=24,
        help="Cache validity period in hours (default: 24)",
    )
    parser.add_argument(
        "--cache-file",
        default="cache/aws_data_cache.json",
        help="Cache file name (default: cache/aws_data_cache.json)",
    )
    parser.add_argument(
        "--cache-stats", action="store_true", help="Show cache statistics and exit"
    )
    parser.add_argument(
        "--clear-cache", action="store_true", help="Clear cache and exit"
    )

    # Information and help
    parser.add_argument(
        "--examples", action="store_true", help="Show usage examples and exit"
    )
    parser.add_argument(
        "--cache-help", action="store_true", help="Show detailed caching help and exit"
    )
    parser.add_argument(
        "--version", action="version", version="AWS Services Reporter v1.3.0"
    )

    # Logging and output
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output (keep only results)",
    )

    return parser.parse_args()


def show_examples() -> None:
    """Display comprehensive usage examples and common commands.

    Prints detailed examples covering basic usage, caching, output formats,
    performance optimization, and common troubleshooting scenarios.
    """
    examples = """
🚀 AWS Services Reporter - Usage Examples

📋 BASIC USAGE:
  python main.py                          # Basic run with defaults
  python main.py --help                   # Show all options

🔄 CACHING EXAMPLES:
  python main.py                          # First run: ~90 seconds, saves cache
  python main.py                          # Second run: ~5 seconds (from cache)
  python main.py --cache-stats             # Show cache information
  python main.py --no-cache                # Force fresh data, ignore cache
  python main.py --cache-hours 1           # Cache valid for 1 hour only
  python main.py --clear-cache             # Clear cache and exit

📊 OUTPUT FORMAT EXAMPLES:
  python main.py --format csv              # Generate CSV files only
  python main.py --format json             # Generate JSON file only
  python main.py --format excel            # Generate Excel file only (requires pandas/openpyxl)
  python main.py --format region-summary   # Generate region summary CSV only
  python main.py --format csv json excel   # Generate all formats
  python main.py --format csv region-summary  # Generate CSV and region summary

🎯 AWS CONFIGURATION EXAMPLES:
  python main.py --profile production      # Use specific AWS profile
  python main.py --region eu-west-1        # Use different AWS region
  python main.py --profile prod --region us-west-2  # Combined AWS settings

⚡ PERFORMANCE EXAMPLES:
  python main.py --max-workers 20          # More concurrent API calls (faster)
  python main.py --max-workers 5           # Fewer concurrent calls (gentler on API limits)
  python main.py --max-retries 5           # More retry attempts for unstable connections

📁 ORGANIZATION EXAMPLES:
  python main.py --output-dir ./reports    # Save files in reports directory
  python main.py --regions-file my_regions.csv --matrix-file my_matrix.csv  # Custom filenames

🔧 DEBUGGING EXAMPLES:
  python main.py --log-level DEBUG         # Detailed logging for troubleshooting
  python main.py --quiet                   # Minimal output, results only
  python main.py --log-level INFO --max-workers 1  # Slow but detailed execution

💡 PRODUCTION EXAMPLES:
  python main.py --format json --quiet --cache-hours 48  # Automated JSON generation
  python main.py --profile prod --output-dir /opt/reports --format csv json  # Production setup

🚀 QUICK START:
  1. python main.py --examples             # See this help
  2. python main.py --cache-help           # Learn about caching
  3. python main.py                        # Run with defaults
  4. python main.py --format json          # Generate JSON output

For more help: python main.py --help
For caching help: python main.py --cache-help
    """
    print(examples)


def show_cache_help() -> None:
    """Display detailed cache system help and configuration information.

    Explains how the intelligent caching system works, performance benefits,
    configuration options, and troubleshooting tips for cache-related issues.
    """
    cache_help = """
🔄 AWS Services Reporter - Caching System

💡 HOW IT WORKS:
The caching system stores AWS data locally to avoid repeated API calls.
On first run, it fetches data (~90 seconds) and saves it.
Subsequent runs load from cache (~5 seconds) - 99% time savings!

📁 CACHE FILE:
• Default: aws_data_cache.json (in output directory)
• Contains: regions, services, timestamps, metadata
• Format: JSON with validation and version info
• Auto-created and managed

⏱️  TIME-TO-LIVE (TTL):
• Default: 24 hours (--cache-hours 24)
• Configurable: 1-8760 hours (1 hour to 1 year)
• Auto-expires: Cache becomes invalid after TTL
• Smart validation: Checks timestamp and data integrity

🚀 PERFORMANCE BENEFITS:
• First run:  ~90 seconds (fresh AWS API data)
• Cache run:  ~5 seconds  (99% time savings)
• Concurrent: Works with multiple workers
• Reliable: Built-in corruption detection

⚙️  CACHE COMMANDS:
  python main.py --cache-stats      # Show cache status, age, size
  python main.py --clear-cache      # Delete cache file
  python main.py --no-cache         # Skip cache, fetch fresh data
  python main.py --cache-hours 6    # Cache valid for 6 hours
  python main.py --cache-file my_cache.json  # Custom cache filename

📊 CACHE STATISTICS:
Use --cache-stats to see:
• Cache file existence and validity
• Age in hours since creation
• File size and total regions/services
• Last update timestamp

🔧 TROUBLESHOOTING:
• Cache corrupted? Use --clear-cache
• Old data? Use --no-cache once, or --cache-hours 1
• Permission errors? Check output directory write access
• Network issues? Cache survives intermittent failures

💯 BEST PRACTICES:
• Let cache work automatically (default behavior)
• Use --cache-stats to monitor cache health
• Clear cache after AWS account changes
• Use longer cache (48+ hours) for stable environments
• Use shorter cache (1-6 hours) for development

🎯 CACHE SCENARIOS:
• Daily reports: --cache-hours 23 (refresh daily)
• Development: --cache-hours 1 (fresh data hourly)
• Production: --cache-hours 48 (stable, efficient)
• One-time run: --no-cache (always fresh)

For examples: python main.py --examples
For all options: python main.py --help
    """
    print(cache_help)
