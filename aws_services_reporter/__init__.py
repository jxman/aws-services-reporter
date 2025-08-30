"""AWS Services Reporter - Modular architecture for AWS service availability analysis.

This package provides comprehensive analysis of AWS service availability across regions
with intelligent caching, multiple output formats, and concurrent data processing.

Modules:
    core: Core configuration, caching, and progress tracking
    aws_client: AWS API interactions and data fetching
    output: Report generation in multiple formats (CSV, JSON, Excel)
    utils: Utility functions and helpers

Author: AWS Services Reporter Team
Version: 1.4.1
License: MIT
"""

from .core.cache import AWSDataCache
from .core.config import Config
from .core.progress import ProgressTracker

__version__ = "1.4.1"
__author__ = "AWS Services Reporter Team"
__license__ = "MIT"

__all__ = [
    "Config",
    "AWSDataCache",
    "ProgressTracker",
]
