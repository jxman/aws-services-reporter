"""CSV output generation for AWS Services Reporter.

Generates CSV reports showing regional service availability and services-regions matrix.
"""

import csv
import logging
from pathlib import Path
from typing import Any, Dict, List

from ..core.config import Config


def create_regions_services_csv(
    config: Config,
    regions: Dict[str, Dict[str, Any]],
    region_services: Dict[str, List[str]],
    service_names: Dict[str, str] = None,
    enhanced_services: Dict[str, Dict[str, Dict[str, Any]]] = None,
    quiet: bool = False,
) -> None:
    """Generate CSV file listing all regions and their available services.

    Args:
        config: Configuration object containing output settings
        regions: Dictionary mapping region codes to region details dictionaries
        region_services: Dictionary mapping region codes to service lists
        service_names: Dictionary mapping service codes to display names
        enhanced_services: Dictionary with enhanced service metadata per region
        quiet: Suppress progress output if True

    Creates:
        CSV file with columns: Region Code, Region Name, Service Code, Service Name, Status, Availability
        Each service gets its own row for each region where it's available
    """
    output_path = Path(config.output_dir) / "csv" / config.regions_filename
    logger = logging.getLogger(__name__)

    if not quiet:
        print(f"  📝 Creating {config.regions_filename}...")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Region Code", "Region Name", "Service Code", "Service Name"
        ])

        # Write data sorted by region code
        for region_code in sorted(regions.keys()):
            region_name = regions[region_code]['name']
            services = sorted(region_services.get(region_code, []))

            for service_code in services:
                service_name = service_names.get(service_code, service_code) if service_names else service_code
                
                writer.writerow([
                    region_code, region_name, service_code, service_name
                ])

    if not quiet:
        total_rows = sum(len(services) for services in region_services.values())
        print(
            f"    ✓ Created {config.regions_filename} ({total_rows:,} service entries)"
        )

    logger.info(f"Created {config.regions_filename} with {len(regions)} regions")


def create_services_regions_matrix_csv(
    config: Config,
    regions: Dict[str, Dict[str, Any]],
    region_services: Dict[str, List[str]],
    service_names: Dict[str, str] = None,
    quiet: bool = False,
) -> None:
    """Generate CSV matrix showing service availability across regions.

    Args:
        config: Configuration object containing output settings
        regions: Dictionary mapping region codes to region details dictionaries
        region_services: Dictionary mapping region codes to service lists
        service_names: Dictionary mapping service codes to display names
        quiet: Suppress progress output if True

    Creates:
        CSV file with services (using full names) as rows and regions as columns
        Cell values: 1 = available, 0 = not available
    """
    output_path = Path(config.output_dir) / "csv" / config.matrix_filename
    logger = logging.getLogger(__name__)

    if not quiet:
        print(f"  📝 Creating {config.matrix_filename}...")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get all unique services and sort them
    all_service_codes = sorted(
        set().union(*region_services.values()) if region_services else []
    )

    # Get sorted region codes
    sorted_regions = sorted(regions.keys())

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        header = ["Service"] + sorted_regions
        writer.writerow(header)

        # Write matrix data
        for service_code in all_service_codes:
            # Use full service name if available, otherwise use service code
            service_display = service_names.get(service_code, service_code) if service_names else service_code
            row = [service_display]
            for region_code in sorted_regions:
                # Check if service is available in this region
                available = (
                    "1" if service_code in region_services.get(region_code, []) else "0"
                )
                row.append(available)
            writer.writerow(row)

    if not quiet:
        print(
            f"    ✓ Created {config.matrix_filename} ({len(all_service_codes)} services × {len(sorted_regions)} regions)"
        )

    logger.info(
        f"Created {config.matrix_filename} matrix: {len(all_service_codes)} services × {len(sorted_regions)} regions"
    )


def create_region_summary_csv(
    config: Config,
    regions: Dict[str, Dict[str, Any]],
    region_services: Dict[str, List[str]],
    quiet: bool = False,
) -> None:
    """Generate CSV file summarizing regions with comprehensive details.

    Args:
        config: Configuration object containing output settings
        regions: Dictionary mapping region codes to region details dictionaries
        region_services: Dictionary mapping region codes to service lists
        quiet: Suppress progress output if True

    Creates:
        CSV file with columns: Region Code, Region Name, Launch Year, Status, 
        Availability Zones, Service Count
        Each region gets one row with comprehensive information
    """
    output_path = Path(config.output_dir) / "csv" / "region_summary.csv"
    logger = logging.getLogger(__name__)

    if not quiet:
        print("  📝 Creating region_summary.csv...")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Region Code", 
            "Region Name", 
            "Availability Zones", 
            "Service Count"
        ])

        # Write data sorted by region code
        for region_code in sorted(regions.keys()):
            region_details = regions[region_code]
            region_name = region_details['name']
            service_count = len(region_services.get(region_code, []))
            az_count = region_details.get('az_count', 0)
            
            writer.writerow([
                region_code, 
                region_name, 
                az_count, 
                service_count
            ])

    if not quiet:
        total_regions = len(regions)
        total_services = sum(len(services) for services in region_services.values())
        avg_services = total_services / total_regions if total_regions > 0 else 0
        print(
            f"    ✓ Created region_summary.csv ({total_regions:,} regions, "
            f"avg {avg_services:.1f} services per region)"
        )

    logger.info(f"Created region_summary.csv with {len(regions)} regions")


def create_service_summary_csv(
    config: Config,
    regions: Dict[str, Dict[str, Any]],
    region_services: Dict[str, List[str]],
    service_names: Dict[str, str] = None,
    quiet: bool = False,
) -> None:
    """Generate CSV file summarizing services with regional coverage statistics.

    Args:
        config: Configuration object containing output settings
        regions: Dictionary mapping region codes to region details dictionaries
        region_services: Dictionary mapping region codes to service lists
        service_names: Dictionary mapping service codes to display names
        quiet: Suppress progress output if True

    Creates:
        CSV file with columns: Service Code, Service Name, Region Count, Coverage %
        Each service gets one row with comprehensive coverage information
    """
    output_path = Path(config.output_dir) / "csv" / "service_summary.csv"
    logger = logging.getLogger(__name__)

    if not quiet:
        print("  📝 Creating service_summary.csv...")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get all unique services and calculate their coverage
    all_service_codes = sorted(set().union(*region_services.values()) if region_services else [])
    total_regions = len(regions)
    
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Service Code", 
            "Service Name", 
            "Region Count", 
            "Coverage %"
        ])

        # Write data sorted by service code
        for service_code in all_service_codes:
            service_name = service_names.get(service_code, service_code) if service_names else service_code
            
            # Count how many regions have this service
            available_regions = [
                region_code for region_code, services in region_services.items()
                if service_code in services
            ]
            region_count = len(available_regions)
            coverage_percent = (region_count / total_regions * 100) if total_regions > 0 else 0
            
            writer.writerow([
                service_code,
                service_name,
                region_count,
                f"{coverage_percent:.1f}"
            ])

    if not quiet:
        print(
            f"    ✓ Created service_summary.csv ({len(all_service_codes):,} services, "
            f"avg {sum(len(services) for services in region_services.values()) / len(all_service_codes):.1f} regions per service)"
        )

    logger.info(f"Created service_summary.csv with {len(all_service_codes)} services")
