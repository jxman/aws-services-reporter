"""Configuration management for AWS Services Reporter.

Provides the Config dataclass and configuration utilities for managing
application settings, CLI arguments, and runtime parameters.
"""

import argparse
import logging
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Config:
    """Configuration settings for the AWS Services Reporter.

    Attributes:
        output_dir: Directory for output files (default: current directory)
        max_workers: Number of concurrent API calls (default: 10)
        regions_filename: CSV filename for regions and services
        matrix_filename: CSV filename for services-regions matrix
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        aws_profile: AWS profile name (None for default)
        aws_region: AWS region for API calls (default: us-east-1)
        max_retries: Maximum retry attempts for failed API calls
        cache_enabled: Enable intelligent caching system
        cache_hours: Cache TTL in hours
        cache_file: Cache file name
        use_rich: Use Rich library for enhanced output
        output_formats: List of output formats to generate
        enhanced_metadata: Enable enhanced metadata fetching
        include_services: List of service patterns to include (wildcards supported)
        exclude_services: List of service patterns to exclude (wildcards supported)
        include_regions: List of region patterns to include (wildcards supported)
        exclude_regions: List of region patterns to exclude (wildcards supported)
        min_services: Minimum number of services required for a region
    """

    output_dir: str = "reports"
    max_workers: int = 10
    regions_filename: str = "regions_services.csv"
    matrix_filename: str = "services_regions_matrix.csv"
    log_level: str = "INFO"
    aws_profile: Optional[str] = None
    aws_region: str = "us-east-1"
    max_retries: int = 3
    cache_enabled: bool = True
    cache_hours: int = 24
    cache_file: str = "cache/aws_data_cache.json"
    use_rich: bool = True
    output_formats: Optional[List[str]] = None
    enhanced_metadata: bool = True
    include_services: Optional[List[str]] = None
    exclude_services: Optional[List[str]] = None
    include_regions: Optional[List[str]] = None
    exclude_regions: Optional[List[str]] = None
    min_services: Optional[int] = None


def create_config_from_args(args: argparse.Namespace) -> Config:
    """Create a Config object from parsed command line arguments.

    Args:
        args: Parsed argument namespace from argparse

    Returns:
        Config object with values from command line arguments
    """
    return Config(
        output_dir=args.output_dir,
        max_workers=args.max_workers,
        regions_filename=args.regions_file,
        matrix_filename=args.matrix_file,
        log_level=args.log_level,
        aws_profile=args.profile,
        aws_region=args.region,
        max_retries=args.max_retries,
        cache_enabled=not args.no_cache,
        cache_hours=args.cache_hours,
        cache_file=args.cache_file,
        use_rich=not getattr(args, "quiet", False),
        output_formats=args.format,
        enhanced_metadata=not getattr(args, "no_enhanced_metadata", False),
        include_services=getattr(args, "include_services", None),
        exclude_services=getattr(args, "exclude_services", None),
        include_regions=getattr(args, "include_regions", None),
        exclude_regions=getattr(args, "exclude_regions", None),
        min_services=getattr(args, "min_services", None),
    )


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration with specified level and formatting.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance

    Note:
        Configures both console and file logging with timestamps
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("aws_services.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)
