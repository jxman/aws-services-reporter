"""CSV output generation for AWS Services Reporter.

Generates CSV reports showing regional service availability and services-regions matrix.
"""

import csv
import logging
from pathlib import Path
from typing import Dict, List

from ..core.config import Config


def create_regions_services_csv(config: Config, regions: Dict[str, str], 
                                region_services: Dict[str, List[str]], quiet: bool = False) -> None:
    """Generate CSV file listing all regions and their available services.
    
    Args:
        config: Configuration object containing output settings
        regions: Dictionary mapping region codes to display names
        region_services: Dictionary mapping region codes to service lists
        quiet: Suppress progress output if True
        
    Creates:
        CSV file with columns: Region Code, Region Name, Service Code
        Each service gets its own row for each region where it's available
    """
    output_path = Path(config.output_dir) / "csv" / config.regions_filename
    logger = logging.getLogger(__name__)
    
    if not quiet:
        print(f"  📝 Creating {config.regions_filename}...")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Region Code", "Region Name", "Service Code"])
        
        # Write data sorted by region code
        for region_code in sorted(regions.keys()):
            region_name = regions[region_code]
            services = sorted(region_services.get(region_code, []))
            
            for service in services:
                writer.writerow([region_code, region_name, service])
    
    if not quiet:
        total_rows = sum(len(services) for services in region_services.values())
        print(f"    ✓ Created {config.regions_filename} ({total_rows:,} service entries)")
    
    logger.info(f"Created {config.regions_filename} with {len(regions)} regions")


def create_services_regions_matrix_csv(config: Config, regions: Dict[str, str], 
                                      region_services: Dict[str, List[str]], quiet: bool = False) -> None:
    """Generate CSV matrix showing service availability across regions.
    
    Args:
        config: Configuration object containing output settings
        regions: Dictionary mapping region codes to display names  
        region_services: Dictionary mapping region codes to service lists
        quiet: Suppress progress output if True
        
    Creates:
        CSV file with services as rows and regions as columns
        Cell values: 1 = available, 0 = not available
    """
    output_path = Path(config.output_dir) / "csv" / config.matrix_filename
    logger = logging.getLogger(__name__)
    
    if not quiet:
        print(f"  📝 Creating {config.matrix_filename}...")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get all unique services and sort them
    all_services = sorted(set().union(*region_services.values()) if region_services else [])
    
    # Get sorted region codes
    sorted_regions = sorted(regions.keys())
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        header = ["Service"] + sorted_regions
        writer.writerow(header)
        
        # Write matrix data
        for service in all_services:
            row = [service]
            for region_code in sorted_regions:
                # Check if service is available in this region
                available = "1" if service in region_services.get(region_code, []) else "0"
                row.append(available)
            writer.writerow(row)
    
    if not quiet:
        print(f"    ✓ Created {config.matrix_filename} ({len(all_services)} services × {len(sorted_regions)} regions)")
    
    logger.info(f"Created {config.matrix_filename} matrix: {len(all_services)} services × {len(sorted_regions)} regions")