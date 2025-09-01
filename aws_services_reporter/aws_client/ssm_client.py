"""AWS SSM Parameter Store client for fetching service availability data.

Handles all interactions with AWS Systems Manager Parameter Store to fetch
region and service availability information with retry logic and error handling.
"""

import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

from ..core.config import Config
from .rss_client import get_rss_region_launch_dates, merge_launch_date_sources


def get_all_parameters_by_path(
    ssm: Any, path: str, max_retries: int = 3
) -> List[Dict[str, Any]]:
    """Fetch all parameters recursively from SSM Parameter Store path.

    Uses pagination and exponential backoff retry logic to handle rate limiting
    and transient failures when fetching large parameter sets.

    Args:
        ssm: Boto3 SSM client instance
        path: Parameter Store path to fetch (e.g., '/aws/service/global-infrastructure')
        max_retries: Maximum retry attempts for failed API calls

    Returns:
        List of parameter dictionaries containing Name, Value, and metadata

    Raises:
        ClientError: If non-retryable AWS API error occurs
        Exception: If maximum retries exceeded or other error occurs
    """
    logger = logging.getLogger(__name__)

    for attempt in range(max_retries):
        try:
            params = []
            next_token = None
            while True:
                kwargs = {
                    "Path": path,
                    "Recursive": False,
                    "MaxResults": 10,  # SSM public params API hard limit
                }
                if next_token:
                    kwargs["NextToken"] = next_token

                resp = ssm.get_parameters_by_path(**kwargs)
                params.extend(resp["Parameters"])

                next_token = resp.get("NextToken")
                if not next_token:
                    break

            return params

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "Throttling" and attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Rate limited for path {path}, waiting {wait_time:.2f}s (attempt {attempt + 1})"
                )
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"AWS API error for path {path}: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error for path {path}: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2**attempt)

    raise Exception(
        f"Failed to fetch parameters for {path} after {max_retries} attempts"
    )


def get_region_details(
    ssm: Any, region_code: str, max_retries: int = 3
) -> Dict[str, Any]:
    """Get comprehensive region information with error handling and retries.

    Args:
        ssm: Boto3 SSM client instance
        region_code: AWS region code (e.g., 'us-east-1')
        max_retries: Maximum retry attempts for failed API calls

    Returns:
        Dictionary with region details:
        {
            'code': str,
            'name': str,
            'launch_date': str,
            'partition': str,
            'az_count': int
        }
        Falls back to minimal data if information cannot be retrieved
    """
    logger = logging.getLogger(__name__)

    result = {
        "code": region_code,
        "name": region_code,  # Fallback to code
        "launch_date": "Unknown",
        "partition": "Unknown",
        "az_count": 0,
    }

    # Get region name
    for attempt in range(max_retries):
        try:
            response = ssm.get_parameter(
                Name=f"/aws/service/global-infrastructure/regions/{region_code}/longName"
            )
            result["name"] = response["Parameter"]["Value"]
            break
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "Throttling" and attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Rate limited for region {region_code} name, waiting {wait_time:.2f}s"
                )
                time.sleep(wait_time)
                continue
            else:
                logger.warning(f"Failed to get name for region {region_code}: {e}")
                break
        except Exception as e:
            logger.warning(f"Unexpected error for region {region_code} name: {e}")
            if attempt == max_retries - 1:
                break
            time.sleep(2**attempt)

    # Get region launch date
    for attempt in range(max_retries):
        try:
            response = ssm.get_parameter(
                Name=f"/aws/service/global-infrastructure/regions/{region_code}/launchDate"
            )
            result["launch_date"] = response["Parameter"]["Value"]
            break
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "Throttling" and attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
            else:
                logger.debug(f"Failed to get launch date for region {region_code}: {e}")
                break
        except Exception as e:
            logger.debug(f"Unexpected error for region {region_code} launch date: {e}")
            if attempt == max_retries - 1:
                break
            time.sleep(2**attempt)

    # Get region partition
    for attempt in range(max_retries):
        try:
            response = ssm.get_parameter(
                Name=f"/aws/service/global-infrastructure/regions/{region_code}/partition"
            )
            result["partition"] = response["Parameter"]["Value"]
            break
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "Throttling" and attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
            else:
                logger.debug(f"Failed to get partition for region {region_code}: {e}")
                break
        except Exception as e:
            logger.debug(f"Unexpected error for region {region_code} partition: {e}")
            if attempt == max_retries - 1:
                break
            time.sleep(2**attempt)

    # Get availability zones count
    try:
        az_params = get_all_parameters_by_path(
            ssm,
            f"/aws/service/global-infrastructure/regions/{region_code}/availability-zones",
            max_retries,
        )
        result["az_count"] = len(az_params)
    except Exception as e:
        logger.debug(f"Failed to get AZ count for region {region_code}: {e}")
        result["az_count"] = 0

    return result


def get_all_regions_and_names(
    config: Config, session: boto3.Session, quiet: bool = False
) -> Dict[str, Dict[str, Any]]:
    """Fetch all AWS regions and their comprehensive details using concurrent processing.

    Integrates data from both AWS SSM Parameter Store and official RSS feed for
    enhanced launch date accuracy and additional metadata.

    Args:
        config: Configuration object with AWS settings
        session: Boto3 session for API calls
        quiet: Suppress progress output if True

    Returns:
        Dictionary mapping region codes to region details dictionaries
        Example: {
            'us-east-1': {
                'name': 'US East (N. Virginia)',
                'launch_date': '2006-08-25',
                'launch_date_source': 'RSS',
                'formatted_date': 'Fri, 25 Aug 2006',
                'announcement_url': 'https://...',
                'partition': 'aws',
                'az_count': 6
            }
        }

    Raises:
        Exception: If region fetching fails completely
    """
    logger = logging.getLogger(__name__)
    if not quiet:
        print("🔍 Fetching AWS regions...")

    ssm = session.client("ssm", region_name=config.aws_region)

    # Fetch RSS launch date data first
    if not quiet:
        print("  ⏳ Fetching launch dates from RSS feed...")
    rss_launch_data = get_rss_region_launch_dates(config)
    if not quiet:
        print(f"  ✓ Retrieved launch dates for {len(rss_launch_data)} regions from RSS")

    # Get all region codes
    if not quiet:
        print("  ⏳ Getting region codes from SSM...")
    region_params = get_all_parameters_by_path(
        ssm, "/aws/service/global-infrastructure/regions", config.max_retries
    )

    if not quiet:
        print(f"  ✓ Found {len(region_params)} regions")
        print(
            f"  ⏳ Fetching region details (using {config.max_workers} concurrent workers)..."
        )

    regions = {}

    # Create separate SSM clients for each thread to avoid session conflicts
    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        # Submit all region detail fetching tasks
        future_to_region = {}
        for region in region_params:
            region_code = region["Value"]
            # Create a new SSM client for each thread
            thread_ssm = session.client("ssm", region_name=config.aws_region)
            future = executor.submit(
                get_region_details, thread_ssm, region_code, config.max_retries
            )
            future_to_region[future] = region_code

        # Collect results as they complete
        completed_count = 0
        for future in as_completed(future_to_region):
            completed_count += 1
            details = future.result()
            code = details["code"]

            # Merge launch date information from RSS and SSM sources
            rss_data = rss_launch_data.get(code)
            merged_launch_data = merge_launch_date_sources(
                details["launch_date"], rss_data
            )

            regions[code] = {
                "name": details["name"],
                "launch_date": merged_launch_data["launch_date"],
                "launch_date_source": merged_launch_data["source"],
                "formatted_date": merged_launch_data["formatted_date"],
                "announcement_url": merged_launch_data["announcement_url"],
                "partition": details["partition"],
                "az_count": details["az_count"],
            }
            if not quiet:
                source_indicator = (
                    "📡"
                    if merged_launch_data["source"] == "RSS"
                    else ("🔧" if merged_launch_data["source"] == "SSM" else "❓")
                )
                print(
                    f"    🌍 {completed_count}/{len(region_params)}: {code} → {details['name']} (AZs: {details['az_count']}, Launch: {merged_launch_data['launch_date']} {source_indicator})"
                )

    logger.info(f"Successfully fetched {len(regions)} region details")
    return regions


def get_services_per_region(
    config: Config, session: boto3.Session, quiet: bool = False
) -> Dict[str, List[str]]:
    """Fetch AWS services available in each region using concurrent processing.

    Args:
        config: Configuration object with AWS settings and concurrency limits
        session: Boto3 session for API calls
        quiet: Suppress progress output if True

    Returns:
        Dictionary mapping region codes to lists of available services
        Example: {'us-east-1': ['ec2', 's3', 'lambda'], 'eu-west-1': ['ec2', 's3']}

    Raises:
        Exception: If service fetching fails completely
    """
    logger = logging.getLogger(__name__)
    if not quiet:
        print("\n🔧 Fetching AWS services availability...")

    ssm = session.client("ssm", region_name=config.aws_region)

    # Get all services
    if not quiet:
        print("  ⏳ Getting service codes from SSM...")
    service_params = get_all_parameters_by_path(
        ssm, "/aws/service/global-infrastructure/services", config.max_retries
    )

    if not quiet:
        print(f"  ✓ Found {len(service_params)} services")
        print("  ⏳ Mapping services to regions...")

    region_services = {}

    for i, service in enumerate(service_params, 1):
        service_code = service["Value"]

        if not quiet:
            print(
                f"    🔧 {i:3d}/{len(service_params)}: {service_code:15s}",
                end="",
                flush=True,
            )

        # Get regions where this service is available
        service_path = (
            f"/aws/service/global-infrastructure/services/{service_code}/regions"
        )
        try:
            svc_regions = get_all_parameters_by_path(
                ssm, service_path, config.max_retries
            )
        except Exception as e:
            logger.warning(f"Failed to get regions for service {service_code}: {e}")
            if not quiet:
                print(" (error - skipping)")
            continue

        if not quiet:
            print(f" (available in {len(svc_regions)} regions)")

        for r in svc_regions:
            region = r["Value"]
            region_services.setdefault(region, []).append(service_code)

    logger.info(f"Mapped {len(service_params)} services across regions")
    return region_services


def get_service_name(ssm: Any, service_code: str, max_retries: int = 3) -> str:
    """Get service display name with error handling and retries.

    Args:
        ssm: Boto3 SSM client instance
        service_code: AWS service code (e.g., 'ec2', 'lambda')
        max_retries: Maximum retry attempts for failed API calls

    Returns:
        Service display name, falls back to service code if name cannot be retrieved
    """
    logger = logging.getLogger(__name__)

    for attempt in range(max_retries):
        try:
            response = ssm.get_parameter(
                Name=f"/aws/service/global-infrastructure/services/{service_code}/longName"
            )
            return response["Parameter"]["Value"]
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "Throttling" and attempt < max_retries - 1:
                wait_time = (2**attempt) + random.uniform(0, 1)
                logger.debug(
                    f"Rate limited for service {service_code}, waiting {wait_time:.2f}s"
                )
                time.sleep(wait_time)
                continue
            else:
                logger.debug(f"Failed to get name for service {service_code}: {e}")
                return service_code  # Fallback to code
        except Exception as e:
            logger.debug(f"Unexpected error for service {service_code}: {e}")
            if attempt == max_retries - 1:
                return service_code  # Fallback to code
            time.sleep(2**attempt)

    return service_code


def get_all_services_with_names(
    config: Config, session: boto3.Session, quiet: bool = False
) -> Dict[str, str]:
    """Fetch all AWS services with their display names using concurrent processing.

    Args:
        config: Configuration object with AWS settings
        session: Boto3 session for API calls
        quiet: Suppress progress output if True

    Returns:
        Dictionary mapping service codes to display names
        Example: {'ec2': 'Amazon Elastic Compute Cloud', 's3': 'Amazon Simple Storage Service'}

    Raises:
        Exception: If service fetching fails completely
    """
    logger = logging.getLogger(__name__)
    if not quiet:
        print("📋 Fetching AWS service names...")

    ssm = session.client("ssm", region_name=config.aws_region)

    # Get all service codes
    if not quiet:
        print("  ⏳ Getting service codes from SSM...")
    service_params = get_all_parameters_by_path(
        ssm, "/aws/service/global-infrastructure/services", config.max_retries
    )

    if not quiet:
        print(f"  ✓ Found {len(service_params)} services")
        print(
            f"  ⏳ Fetching service names (using {config.max_workers} concurrent workers)..."
        )

    services = {}

    # Create separate SSM clients for each thread to avoid session conflicts
    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        # Submit all service name fetching tasks
        future_to_service = {}
        for service in service_params:
            service_code = service["Value"]
            # Create a new SSM client for each thread
            thread_ssm = session.client("ssm", region_name=config.aws_region)
            future = executor.submit(
                get_service_name, thread_ssm, service_code, config.max_retries
            )
            future_to_service[future] = service_code

        # Collect results as they complete
        completed_count = 0
        for future in as_completed(future_to_service):
            completed_count += 1
            service_code = future_to_service[future]
            service_name = future.result()
            services[service_code] = service_name
            if not quiet:
                print(
                    f"    📋 {completed_count}/{len(service_params)}: {service_code} → {service_name}"
                )

    logger.info(f"Successfully fetched {len(services)} service names")
    return services


def get_services_per_region_enhanced(
    config: Config, session: boto3.Session, quiet: bool = False
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Fetch AWS services per region with enhanced service names (streamlined version).

    This version only fetches data that actually exists in AWS Parameter Store.
    Currently, only service longNames are available - categories, descriptions,
    launch dates, and status are not available in the public Parameter Store.

    Args:
        config: Configuration object with AWS settings and concurrency limits
        session: Boto3 session for API calls
        quiet: Suppress progress output if True

    Returns:
        Dictionary mapping region codes to service dictionaries with available metadata
        Example: {
            'us-east-1': {
                'ec2': {
                    'name': 'Amazon Elastic Compute Cloud (EC2)',
                    'status': 'available',
                    'availability': 'Available'
                }
            }
        }

    Raises:
        Exception: If service fetching fails completely
    """
    logger = logging.getLogger(__name__)
    if not quiet:
        print("\n🔧 Creating enhanced service mapping with full names...")

    # Get basic region services mapping
    region_services = get_services_per_region(config, session, quiet)

    # Get service names (this is the only enhanced metadata actually available)
    service_names = get_all_services_with_names(config, session, quiet)

    if not quiet:
        print("  ⏳ Building enhanced service metadata...")

    enhanced_services = {}

    # Create enhanced metadata with only available data
    for region_code, services in region_services.items():
        enhanced_services[region_code] = {}
        for service_code in services:
            enhanced_services[region_code][service_code] = {
                # Only include data we can actually retrieve
                "name": service_names.get(service_code, service_code),
                "status": "available",  # If it's in the region, it's available
            }

    total_service_entries = sum(
        len(services) for services in enhanced_services.values()
    )

    if not quiet:
        print(
            f"  ✓ Enhanced service metadata complete: {len(enhanced_services)} regions, {total_service_entries:,} service entries"
        )

    logger.info(
        f"Created enhanced service metadata for {len(enhanced_services)} regions ({total_service_entries:,} entries)"
    )
    return enhanced_services


def get_all_services() -> List[str]:
    """Fetch and return sorted list of all AWS service codes.

    Returns:
        Sorted list of AWS service codes (e.g., ['ec2', 'lambda', 's3'])

    Raises:
        Exception: If service fetching fails
    """
    ssm = boto3.client("ssm", region_name="us-east-1")
    service_params = get_all_parameters_by_path(
        ssm, "/aws/service/global-infrastructure/services"
    )
    return sorted([svc["Value"] for svc in service_params])
