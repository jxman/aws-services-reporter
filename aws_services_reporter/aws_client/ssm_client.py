"""AWS SSM Parameter Store client for fetching service availability data.

Handles all interactions with AWS Systems Manager Parameter Store to fetch
region and service availability information with retry logic and error handling.
"""

import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple

import boto3
from botocore.exceptions import ClientError

from ..core.config import Config


def get_all_parameters_by_path(ssm: Any, path: str, max_retries: int = 3) -> List[Dict[str, Any]]:
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
                    "MaxResults": 10   # SSM public params API hard limit
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
            error_code = e.response['Error']['Code']
            if error_code == 'Throttling' and attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limited for path {path}, waiting {wait_time:.2f}s (attempt {attempt + 1})")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"AWS API error for path {path}: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error for path {path}: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    
    raise Exception(f"Failed to fetch parameters for {path} after {max_retries} attempts")


def get_region_name(ssm: Any, region_code: str, max_retries: int = 3) -> Tuple[str, str]:
    """Get region name with error handling and retries.
    
    Args:
        ssm: Boto3 SSM client instance
        region_code: AWS region code (e.g., 'us-east-1')
        max_retries: Maximum retry attempts for failed API calls
        
    Returns:
        Tuple of (region_code, region_name)
        Falls back to (region_code, region_code) if name cannot be retrieved
    """
    logger = logging.getLogger(__name__)
    
    for attempt in range(max_retries):
        try:
            response = ssm.get_parameter(
                Name=f"/aws/service/global-infrastructure/regions/{region_code}/longName"
            )
            return region_code, response["Parameter"]["Value"]
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'Throttling' and attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limited for region {region_code}, waiting {wait_time:.2f}s")
                time.sleep(wait_time)
                continue
            else:
                logger.warning(f"Failed to get name for region {region_code}: {e}")
                return region_code, region_code  # Fallback to code
        except Exception as e:
            logger.warning(f"Unexpected error for region {region_code}: {e}")
            if attempt == max_retries - 1:
                return region_code, region_code  # Fallback to code
            time.sleep(2 ** attempt)
    
    return region_code, region_code


def get_all_regions_and_names(config: Config, session: boto3.Session, quiet: bool = False) -> Dict[str, str]:
    """Fetch all AWS regions and their display names using concurrent processing.
    
    Args:
        config: Configuration object with AWS settings
        session: Boto3 session for API calls
        quiet: Suppress progress output if True
        
    Returns:
        Dictionary mapping region codes to display names
        Example: {'us-east-1': 'US East (N. Virginia)'}
        
    Raises:
        Exception: If region fetching fails completely
    """
    logger = logging.getLogger(__name__)
    if not quiet:
        print("🔍 Fetching AWS regions...")
    
    ssm = session.client("ssm", region_name=config.aws_region)

    # Get all region codes
    if not quiet:
        print("  ⏳ Getting region codes from SSM...")
    region_params = get_all_parameters_by_path(ssm, "/aws/service/global-infrastructure/regions", config.max_retries)
    
    if not quiet:
        print(f"  ✓ Found {len(region_params)} regions")
        print(f"  ⏳ Fetching region names (using {config.max_workers} concurrent workers)...")

    regions = {}
    
    # Create separate SSM clients for each thread to avoid session conflicts
    with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        # Submit all region name fetching tasks
        future_to_region = {}
        for region in region_params:
            region_code = region["Value"]
            # Create a new SSM client for each thread
            thread_ssm = session.client("ssm", region_name=config.aws_region)
            future = executor.submit(get_region_name, thread_ssm, region_code, config.max_retries)
            future_to_region[future] = region_code
        
        # Collect results as they complete
        completed_count = 0
        for future in as_completed(future_to_region):
            completed_count += 1
            code, name = future.result()
            regions[code] = name
            if not quiet:
                print(f"    🌍 {completed_count}/{len(region_params)}: {code} → {name}")
    
    logger.info(f"Successfully fetched {len(regions)} region names")
    return regions


def get_services_per_region(config: Config, session: boto3.Session, quiet: bool = False) -> Dict[str, List[str]]:
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
            print(f"    🔧 {i:3d}/{len(service_params)}: {service_code:15s}", end="", flush=True)
        
        # Get regions where this service is available
        service_path = f"/aws/service/global-infrastructure/services/{service_code}/regions"
        try:
            svc_regions = get_all_parameters_by_path(ssm, service_path, config.max_retries)
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