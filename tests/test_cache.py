"""Tests for AWS data caching functionality."""

import json
import os

# Import the classes we're testing
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from aws_services_reporter.core.cache import AWSDataCache
from aws_services_reporter.core.config import Config


class TestAWSDataCache:
    """Test cases for AWSDataCache class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = Path(self.temp_dir) / "test_cache.json"
        self.cache = AWSDataCache(str(self.cache_file), cache_hours=24)

        # Sample test data (updated to match current data structure)
        self.test_regions = {
            "us-east-1": {
                "name": "US East (N. Virginia)",
                "launch_date": "2006-08-25",
                "partition": "aws",
                "az_count": 3,
            },
            "eu-west-1": {
                "name": "Europe (Ireland)",
                "launch_date": "2007-10-10",
                "partition": "aws",
                "az_count": 3,
            },
            "ap-southeast-1": {
                "name": "Asia Pacific (Singapore)",
                "launch_date": "2010-04-28",
                "partition": "aws",
                "az_count": 3,
            },
        }

        self.test_region_services = {
            "us-east-1": ["ec2", "s3", "lambda"],
            "eu-west-1": ["ec2", "s3"],
            "ap-southeast-1": ["ec2"],
        }

        self.test_metadata = {"fetch_duration": 89.5, "aws_profile": "test-profile"}

    def teardown_method(self):
        """Clean up test fixtures."""
        if self.cache_file.exists():
            self.cache_file.unlink()
        os.rmdir(self.temp_dir)

    def test_cache_file_creation(self):
        """Test cache file is created with correct structure."""
        # Save data to cache (using new signature with metadata parameter)
        result = self.cache.save(
            self.test_regions, self.test_region_services, metadata=self.test_metadata
        )

        assert result is True
        assert self.cache_file.exists()

        # Verify file structure
        with open(self.cache_file, "r") as f:
            cache_data = json.load(f)

        assert "timestamp" in cache_data
        assert "regions" in cache_data
        assert "region_services" in cache_data
        assert "metadata" in cache_data
        assert "cache_info" in cache_data

        # Verify data integrity
        assert cache_data["regions"] == self.test_regions
        assert cache_data["region_services"] == self.test_region_services
        assert cache_data["metadata"] == self.test_metadata

    def test_cache_validity_check(self):
        """Test cache validity checking with TTL."""
        # Save fresh data
        self.cache.save(self.test_regions, self.test_region_services)
        assert self.cache.is_valid() is True

        # Test expired cache
        expired_cache = AWSDataCache(str(self.cache_file), cache_hours=0)
        assert expired_cache.is_valid() is False

    def test_cache_load_valid(self):
        """Test loading data from valid cache."""
        # Save and load data
        self.cache.save(
            self.test_regions, self.test_region_services, metadata=self.test_metadata
        )
        loaded_data = self.cache.load()

        assert loaded_data is not None
        assert loaded_data["regions"] == self.test_regions
        assert loaded_data["region_services"] == self.test_region_services
        assert loaded_data["metadata"] == self.test_metadata

    def test_cache_load_invalid(self):
        """Test loading data from invalid cache."""
        # Create expired cache
        expired_cache = AWSDataCache(str(self.cache_file), cache_hours=0)
        self.cache.save(self.test_regions, self.test_region_services)

        loaded_data = expired_cache.load()
        assert loaded_data is None

    def test_cache_clear(self):
        """Test cache clearing functionality."""
        # Create cache file
        self.cache.save(self.test_regions, self.test_region_services)
        assert self.cache_file.exists()

        # Clear cache
        result = self.cache.clear()
        assert result is True
        assert not self.cache_file.exists()

    def test_cache_stats(self):
        """Test cache statistics generation."""
        # Test non-existent cache
        stats = self.cache.get_stats()
        assert stats["exists"] is False

        # Create cache and test stats
        self.cache.save(self.test_regions, self.test_region_services)
        stats = self.cache.get_stats()

        assert stats["exists"] is True
        assert stats["valid"] is True
        assert "age_hours" in stats
        assert "file_size" in stats
        assert "cache_info" in stats
        assert "timestamp" in stats

    def test_corrupted_cache_handling(self):
        """Test handling of corrupted cache files."""
        # Create corrupted cache file
        with open(self.cache_file, "w") as f:
            f.write("invalid json content")

        assert self.cache.is_valid() is False
        assert self.cache.load() is None

        # Stats should handle corruption gracefully
        stats = self.cache.get_stats()
        assert stats["exists"] is True
        assert "error" in stats

    def test_cache_metadata_generation(self):
        """Test automatic metadata generation in cache."""
        self.cache.save(
            self.test_regions, self.test_region_services, self.test_metadata
        )

        with open(self.cache_file, "r") as f:
            cache_data = json.load(f)

        cache_info = cache_data["cache_info"]
        assert cache_info["version"] == "1.3.0"
        assert cache_info["total_regions"] == len(self.test_regions)
        assert cache_info["total_services"] == 3  # ec2, s3, lambda
        assert "cache_file_size" in cache_info


if __name__ == "__main__":
    pytest.main([__file__])
