"""Tests for AWS integration using moto mocking."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import boto3
import pytest
from moto import mock_aws

# Import functions to test
sys.path.insert(0, str(Path(__file__).parent.parent))
from aws_services_reporter.aws_client.session import create_session
from aws_services_reporter.aws_client.ssm_client import (
    get_all_parameters_by_path,
    get_all_regions_and_names,
    get_region_name,
    get_services_per_region,
)
from aws_services_reporter.core.config import Config


@mock_aws
class TestAWSIntegration:
    """Test AWS integration with mocked services."""

    def setup_method(self, method):
        """Set up test fixtures with mocked AWS services."""
        # Create mock SSM client and parameters
        self.ssm = boto3.client("ssm", region_name="us-east-1")

        # Mock region parameters
        self.test_regions = {
            "us-east-1": "US East (N. Virginia)",
            "eu-west-1": "Europe (Ireland)",
            "ap-southeast-1": "Asia Pacific (Singapore)",
        }

        # Mock service-to-region mapping
        self.test_services = {
            "ec2": ["us-east-1", "eu-west-1", "ap-southeast-1"],
            "s3": ["us-east-1", "eu-west-1"],
            "lambda": ["us-east-1"],
        }

        # Create SSM parameters for regions (using test paths instead of reserved AWS paths)
        for region_code, region_name in self.test_regions.items():
            self.ssm.put_parameter(
                Name=f"/test/infrastructure/regions/{region_code}",
                Value=region_code,
                Type="String",
            )
            self.ssm.put_parameter(
                Name=f"/test/infrastructure/regions/{region_code}/longName",
                Value=region_name,
                Type="String",
            )

        # Create SSM parameters for services (using test paths)
        for service_code, available_regions in self.test_services.items():
            self.ssm.put_parameter(
                Name=f"/test/infrastructure/services/{service_code}",
                Value=service_code,
                Type="String",
            )

            for region in available_regions:
                self.ssm.put_parameter(
                    Name=f"/test/infrastructure/services/{service_code}/regions/{region}",
                    Value=region,
                    Type="String",
                )

    def test_get_all_parameters_by_path(self):
        """Test SSM parameter fetching with pagination."""
        # Test region parameter fetching
        params = get_all_parameters_by_path(self.ssm, "/test/infrastructure/regions")

        assert len(params) == len(self.test_regions)
        param_values = [p["Value"] for p in params]

        for region_code in self.test_regions.keys():
            assert region_code in param_values

    def test_get_region_name(self):
        """Test individual region name fetching."""
        # Patch the function to use test paths
        import unittest.mock

        with unittest.mock.patch.object(self.ssm, "get_parameter") as mock_get:
            mock_get.return_value = {"Parameter": {"Value": "US East (N. Virginia)"}}
            region_code, region_name = get_region_name(self.ssm, "us-east-1")

            assert region_code == "us-east-1"
            assert region_name == "US East (N. Virginia)"

    def test_get_region_name_error_handling(self):
        """Test region name fetching with non-existent region."""
        region_code, region_name = get_region_name(self.ssm, "non-existent-region")

        # Should fallback to region code
        assert region_code == "non-existent-region"
        assert region_name == "non-existent-region"

    @pytest.mark.skip(
        reason="These functions use real AWS parameter paths - need integration environment"
    )
    def test_get_all_regions_and_names(self):
        """Test complete region fetching functionality."""
        config = Config(max_workers=2, max_retries=1, aws_region="us-east-1")
        session = boto3.Session()

        regions = get_all_regions_and_names(config, session, quiet=True)

        assert len(regions) == len(self.test_regions)

        for region_code, expected_name in self.test_regions.items():
            assert regions[region_code] == expected_name

    @pytest.mark.skip(
        reason="These functions use real AWS parameter paths - need integration environment"
    )
    def test_get_services_per_region(self):
        """Test service-to-region mapping functionality."""
        config = Config(max_retries=1, aws_region="us-east-1")
        session = boto3.Session()

        region_services = get_services_per_region(config, session, quiet=True)

        # Verify service distribution
        assert "ec2" in region_services["us-east-1"]
        assert "ec2" in region_services["eu-west-1"]
        assert "ec2" in region_services["ap-southeast-1"]

        assert "s3" in region_services["us-east-1"]
        assert "s3" in region_services["eu-west-1"]
        assert "s3" not in region_services["ap-southeast-1"]

        assert "lambda" in region_services["us-east-1"]
        assert "lambda" not in region_services["eu-west-1"]

    def test_parameter_pagination(self):
        """Test pagination handling for large parameter sets."""
        # Create many parameters to test pagination
        for i in range(15):  # More than the 10 limit
            self.ssm.put_parameter(
                Name=f"/test/infrastructure/test-regions/region-{i:02d}",
                Value=f"region-{i:02d}",
                Type="String",
            )

        params = get_all_parameters_by_path(
            self.ssm, "/test/infrastructure/test-regions"
        )

        assert len(params) == 15  # Should get all parameters despite pagination

    def test_create_session_with_profile(self):
        """Test session creation with AWS profile."""
        config = Config(aws_profile="test-profile")

        with patch("boto3.Session") as mock_session:
            create_session(config)
            mock_session.assert_called_once_with(profile_name="test-profile")

    def test_create_session_without_profile(self):
        """Test session creation without AWS profile."""
        config = Config(aws_profile=None)

        with patch("boto3.Session") as mock_session:
            create_session(config)
            mock_session.assert_called_once_with()


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_retry_mechanism(self):
        """Test retry mechanism with simulated throttling."""
        mock_ssm = MagicMock()

        # Simulate throttling then success
        from botocore.exceptions import ClientError

        throttling_error = ClientError(
            error_response={"Error": {"Code": "Throttling"}},
            operation_name="GetParametersByPath",
        )

        mock_ssm.get_parameters_by_path.side_effect = [
            throttling_error,
            throttling_error,
            {"Parameters": [{"Name": "test", "Value": "value"}], "NextToken": None},
        ]

        # Should eventually succeed after retries
        with patch("time.sleep"):  # Speed up test by mocking sleep
            result = get_all_parameters_by_path(mock_ssm, "/test/path", max_retries=3)
            assert len(result) == 1
            assert mock_ssm.get_parameters_by_path.call_count == 3

    def test_non_retryable_error(self):
        """Test handling of non-retryable errors."""
        mock_ssm = MagicMock()

        from botocore.exceptions import ClientError

        access_denied_error = ClientError(
            error_response={"Error": {"Code": "AccessDenied"}},
            operation_name="GetParametersByPath",
        )

        mock_ssm.get_parameters_by_path.side_effect = access_denied_error

        # Should raise immediately for non-retryable errors
        with pytest.raises(ClientError):
            get_all_parameters_by_path(mock_ssm, "/test/path", max_retries=3)


if __name__ == "__main__":
    pytest.main([__file__])
