"""Filtering utilities for AWS Services Reporter.

Provides filtering capabilities for regions and services based on patterns,
wildcards, and other criteria.
"""

import fnmatch
import logging
from typing import Any, Dict, List, Optional, Set


def apply_service_filters(
    region_services: Dict[str, List[str]],
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
) -> Dict[str, List[str]]:
    """Apply service filters to region services data.

    Args:
        region_services: Dictionary mapping region codes to service lists
        include_patterns: List of patterns to include (wildcards supported)
        exclude_patterns: List of patterns to exclude (wildcards supported)

    Returns:
        Filtered region services dictionary
    """
    logger = logging.getLogger(__name__)

    if not include_patterns and not exclude_patterns:
        return region_services

    # Get all unique services
    all_services = set()
    for services in region_services.values():
        all_services.update(services)

    filtered_services = set(all_services)

    # Apply include filters
    if include_patterns:
        included = set()
        for pattern in include_patterns:
            matched = [
                s for s in all_services if fnmatch.fnmatch(s.lower(), pattern.lower())
            ]
            included.update(matched)
            logger.debug(f"Include pattern '{pattern}' matched {len(matched)} services")

        filtered_services = included
        logger.info(
            f"Include filters reduced services from {len(all_services)} to {len(filtered_services)}"
        )

    # Apply exclude filters
    if exclude_patterns:
        excluded = set()
        for pattern in exclude_patterns:
            matched = [
                s
                for s in filtered_services
                if fnmatch.fnmatch(s.lower(), pattern.lower())
            ]
            excluded.update(matched)
            logger.debug(f"Exclude pattern '{pattern}' matched {len(matched)} services")

        filtered_services -= excluded
        logger.info(f"Exclude filters reduced services to {len(filtered_services)}")

    # Filter region services
    filtered_region_services = {}
    for region, services in region_services.items():
        filtered_services_for_region = [s for s in services if s in filtered_services]
        if filtered_services_for_region:  # Only include regions with services
            filtered_region_services[region] = filtered_services_for_region

    logger.info(
        f"Service filtering: {len(region_services)} → {len(filtered_region_services)} regions"
    )
    return filtered_region_services


def apply_region_filters(
    regions: Dict[str, Dict[str, Any]],
    region_services: Dict[str, List[str]],
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    min_services: Optional[int] = None,
) -> tuple[Dict[str, Dict[str, Any]], Dict[str, List[str]]]:
    """Apply region filters to regions and services data.

    Args:
        regions: Dictionary mapping region codes to region details
        region_services: Dictionary mapping region codes to service lists
        include_patterns: List of patterns to include (wildcards supported)
        exclude_patterns: List of patterns to exclude (wildcards supported)
        min_services: Minimum number of services required for a region

    Returns:
        Tuple of (filtered regions, filtered region services)
    """
    logger = logging.getLogger(__name__)

    filtered_regions = set(regions.keys())

    # Apply include filters
    if include_patterns:
        included = set()
        for pattern in include_patterns:
            # Match against region codes and names
            for region_code, region_details in regions.items():
                region_name = region_details.get("name", "").lower()
                if fnmatch.fnmatch(
                    region_code.lower(), pattern.lower()
                ) or fnmatch.fnmatch(region_name, pattern.lower()):
                    included.add(region_code)

        filtered_regions = included
        logger.info(
            f"Include filters: {len(regions)} → {len(filtered_regions)} regions"
        )

    # Apply exclude filters
    if exclude_patterns:
        excluded = set()
        for pattern in exclude_patterns:
            for region_code in filtered_regions:
                region_name = regions[region_code].get("name", "").lower()
                if fnmatch.fnmatch(
                    region_code.lower(), pattern.lower()
                ) or fnmatch.fnmatch(region_name, pattern.lower()):
                    excluded.add(region_code)

        filtered_regions -= excluded
        logger.info(f"Exclude filters: regions reduced to {len(filtered_regions)}")

    # Apply minimum services filter
    if min_services is not None:
        regions_with_min_services = set()
        for region_code in filtered_regions:
            service_count = len(region_services.get(region_code, []))
            if service_count >= min_services:
                regions_with_min_services.add(region_code)

        filtered_regions = regions_with_min_services
        logger.info(
            f"Min services filter ({min_services}): regions reduced to {len(filtered_regions)}"
        )

    # Create filtered dictionaries
    filtered_regions_dict = {
        region: details
        for region, details in regions.items()
        if region in filtered_regions
    }

    filtered_region_services = {
        region: services
        for region, services in region_services.items()
        if region in filtered_regions
    }

    logger.info(
        f"Region filtering complete: {len(regions)} → {len(filtered_regions_dict)} regions"
    )
    return filtered_regions_dict, filtered_region_services


def get_filter_summary(
    original_regions_count: int,
    original_services_count: int,
    filtered_regions_count: int,
    filtered_services_count: int,
    include_services: Optional[List[str]] = None,
    exclude_services: Optional[List[str]] = None,
    include_regions: Optional[List[str]] = None,
    exclude_regions: Optional[List[str]] = None,
    min_services: Optional[int] = None,
) -> str:
    """Generate a summary of applied filters.

    Args:
        original_regions_count: Original number of regions
        original_services_count: Original number of services
        filtered_regions_count: Number of regions after filtering
        filtered_services_count: Number of services after filtering
        include_services: Service include patterns
        exclude_services: Service exclude patterns
        include_regions: Region include patterns
        exclude_regions: Region exclude patterns
        min_services: Minimum services threshold

    Returns:
        Formatted filter summary string
    """
    lines = ["🔍 Applied Filters:"]

    if include_services:
        lines.append(f"  • Include services: {', '.join(include_services)}")
    if exclude_services:
        lines.append(f"  • Exclude services: {', '.join(exclude_services)}")
    if include_regions:
        lines.append(f"  • Include regions: {', '.join(include_regions)}")
    if exclude_regions:
        lines.append(f"  • Exclude regions: {', '.join(exclude_regions)}")
    if min_services:
        lines.append(f"  • Min services per region: {min_services}")

    lines.append("")
    lines.append("📊 Filter Results:")
    lines.append(
        f"  • Regions: {original_regions_count:,} → {filtered_regions_count:,}"
    )
    lines.append(
        f"  • Services: {original_services_count:,} → {filtered_services_count:,}"
    )

    if filtered_regions_count < original_regions_count:
        reduction_pct = (
            (original_regions_count - filtered_regions_count) / original_regions_count
        ) * 100
        lines.append(f"  • Regions filtered: {reduction_pct:.1f}%")

    if filtered_services_count < original_services_count:
        reduction_pct = (
            (original_services_count - filtered_services_count)
            / original_services_count
        ) * 100
        lines.append(f"  • Services filtered: {reduction_pct:.1f}%")

    return "\n".join(lines)


def validate_filter_patterns(patterns: List[str]) -> bool:
    """Validate filter patterns for basic syntax.

    Args:
        patterns: List of patterns to validate

    Returns:
        True if all patterns are valid, False otherwise
    """
    if not patterns:
        return True

    for pattern in patterns:
        if not isinstance(pattern, str) or not pattern.strip():
            return False

    return True
