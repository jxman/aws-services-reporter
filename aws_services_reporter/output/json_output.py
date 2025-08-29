"""JSON output generation for AWS Services Reporter.

Generates comprehensive JSON reports with statistics, metadata, and structured data.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.config import Config


def _get_region_status(partition: str) -> str:
    """Get human-readable status from partition.

    Args:
        partition: AWS partition (e.g., 'aws', 'aws-gov', 'aws-cn')

    Returns:
        Human-readable status string
    """
    if partition == "aws":
        return "Active"
    elif partition == "aws-gov":
        return "Gov Cloud"
    elif partition == "aws-cn":
        return "China"
    else:
        return (
            partition.replace("aws-", "").title()
            if partition.startswith("aws-")
            else partition.title()
        )


def create_json_output(
    config: Config,
    regions: Dict[str, Dict[str, Any]],
    region_services: Dict[str, List[str]],
    service_names: Optional[Dict[str, str]] = None,
    enhanced_services: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    quiet: bool = False,
) -> bool:
    """Generate comprehensive JSON output with statistics and metadata.

    Args:
        config: Configuration object containing output settings
        regions: Dictionary mapping region codes to region details dictionaries
        region_services: Dictionary mapping region codes to service lists
        service_names: Dictionary mapping service codes to display names
        enhanced_services: Dictionary with enhanced service metadata per region
        metadata: Optional metadata about the data fetch operation
        quiet: Suppress progress output if True

    Returns:
        True if JSON file was successfully created, False otherwise

    Creates:
        JSON file with complete AWS service data including:
        - Regional service availability with comprehensive details
        - Service statistics and coverage
        - Generation metadata and timestamps
    """
    output_path = (
        Path(config.output_dir) / "json" / f"{Path(config.regions_filename).stem}.json"
    )
    logger = logging.getLogger(__name__)

    if not quiet:
        print(f"  📝 Creating JSON output...")

    # Prepare comprehensive data structure
    all_services = sorted(
        set().union(*region_services.values()) if region_services else []
    )

    # Calculate statistics with full service names
    service_stats = {}
    for service_code in all_services:
        available_regions = [
            region
            for region, services in region_services.items()
            if service_code in services
        ]
        coverage_pct = (len(available_regions) / len(regions)) * 100 if regions else 0

        # Use full service name as key if available
        service_key = (
            service_names.get(service_code, service_code)
            if service_names
            else service_code
        )

        service_stats[service_key] = {
            "service_code": service_code,
            "available_in": len(available_regions),
            "coverage_percentage": round(coverage_pct, 1),
            "regions": sorted(available_regions),
        }

    # Find most/least available services
    if service_stats:
        most_available = max(
            service_stats.keys(), key=lambda x: service_stats[x]["available_in"]
        )
        least_available = min(
            service_stats.keys(), key=lambda x: service_stats[x]["available_in"]
        )
    else:
        most_available = least_available = None

    # Calculate average services per region
    total_service_instances = sum(
        len(services) for services in region_services.values()
    )
    avg_services = total_service_instances / len(regions) if regions else 0

    # Build comprehensive JSON structure
    json_data = {
        "generated_at": datetime.now().isoformat(),
        "generator": {
            "name": "AWS Services Reporter",
            "version": "1.3.0",
            "url": "https://github.com/aws-services-reporter",
        },
        "summary": {
            "total_regions": len(regions),
            "total_services": len(all_services),
            "total_service_instances": total_service_instances,
            "avg_services_per_region": round(avg_services, 1),
            "most_available_service": most_available,
            "least_available_service": least_available,
        },
        "regions": {
            region_code: {
                "name": region_details["name"],
                "launch_year": (
                    region_details.get("launch_date", "Unknown").split("-")[0]
                    if region_details.get("launch_date", "Unknown") != "Unknown"
                    else "Unknown"
                ),
                "status": _get_region_status(
                    region_details.get("partition", "Unknown")
                ),
                "partition": region_details.get("partition", "Unknown"),
                "availability_zones": region_details.get("az_count", 0),
                "service_count": len(region_services.get(region_code, [])),
                "services": [
                    {
                        "code": service_code,
                        "name": (
                            service_names.get(service_code, service_code)
                            if service_names
                            else service_code
                        ),
                    }
                    for service_code in sorted(region_services.get(region_code, []))
                ],
            }
            for region_code, region_details in sorted(regions.items())
        },
        "services": service_stats,
        "metadata": metadata or {},
    }

    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON file with pretty formatting
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, sort_keys=True)

        # Get file size for both display and logging
        file_size = output_path.stat().st_size

        if not quiet:
            print(f"    ✓ Created JSON output ({file_size:,} bytes)")

        logger.info(f"Created JSON output: {output_path} ({file_size:,} bytes)")
        return True

    except Exception as e:
        if not quiet:
            print(f"  ❌ Failed to create JSON output: {e}")
        logger.error(f"Failed to create JSON output: {e}")
        return False
