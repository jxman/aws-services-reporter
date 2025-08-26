"""JSON output generation for AWS Services Reporter.

Generates comprehensive JSON reports with statistics, metadata, and structured data.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.config import Config


def create_json_output(config: Config, regions: Dict[str, str], region_services: Dict[str, List[str]], 
                      metadata: Optional[Dict[str, Any]] = None, quiet: bool = False) -> bool:
    """Generate comprehensive JSON output with statistics and metadata.
    
    Args:
        config: Configuration object containing output settings
        regions: Dictionary mapping region codes to display names
        region_services: Dictionary mapping region codes to service lists
        metadata: Optional metadata about the data fetch operation
        quiet: Suppress progress output if True
        
    Returns:
        True if JSON file was successfully created, False otherwise
        
    Creates:
        JSON file with complete AWS service data including:
        - Regional service availability
        - Service statistics and coverage
        - Generation metadata and timestamps
    """
    output_path = Path(config.output_dir) / "json" / f"{Path(config.regions_filename).stem}.json"
    logger = logging.getLogger(__name__)
    
    if not quiet:
        print(f"  📝 Creating JSON output...")
    
    # Prepare comprehensive data structure
    all_services = sorted(set().union(*region_services.values()) if region_services else [])
    
    # Calculate statistics
    service_stats = {}
    for service in all_services:
        available_regions = [region for region, services in region_services.items() if service in services]
        coverage_pct = (len(available_regions) / len(regions)) * 100 if regions else 0
        service_stats[service] = {
            "available_in": len(available_regions),
            "coverage_percentage": round(coverage_pct, 1),
            "regions": sorted(available_regions)
        }
    
    # Find most/least available services
    if service_stats:
        most_available = max(service_stats.keys(), key=lambda x: service_stats[x]["available_in"])
        least_available = min(service_stats.keys(), key=lambda x: service_stats[x]["available_in"])
    else:
        most_available = least_available = None
    
    # Calculate average services per region
    total_service_instances = sum(len(services) for services in region_services.values())
    avg_services = total_service_instances / len(regions) if regions else 0
    
    # Build comprehensive JSON structure
    json_data = {
        "generated_at": datetime.now().isoformat(),
        "generator": {
            "name": "AWS Services Reporter",
            "version": "1.3.0",
            "url": "https://github.com/aws-services-reporter"
        },
        "summary": {
            "total_regions": len(regions),
            "total_services": len(all_services),
            "total_service_instances": total_service_instances,
            "avg_services_per_region": round(avg_services, 1),
            "most_available_service": most_available,
            "least_available_service": least_available
        },
        "regions": {
            region_code: {
                "name": region_name,
                "service_count": len(region_services.get(region_code, [])),
                "services": sorted(region_services.get(region_code, []))
            }
            for region_code, region_name in sorted(regions.items())
        },
        "services": service_stats,
        "metadata": metadata or {}
    }
    
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON file with pretty formatting
        with open(output_path, 'w', encoding='utf-8') as f:
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