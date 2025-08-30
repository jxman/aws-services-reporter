"""RSS feed client for fetching AWS region launch dates from official RSS feed.

This module fetches and parses AWS region launch dates from the official AWS
documentation RSS feed to supplement SSM Parameter Store data with additional
context and potentially more accurate launch information.
"""

import logging
import re
from datetime import datetime
from typing import Dict, Optional

try:
    import defusedxml.ElementTree as ET
except ImportError:
    import warnings
    import xml.etree.ElementTree as ET  # nosec B405

    warnings.warn(
        "defusedxml not available, using xml.etree.ElementTree. "
        "Install defusedxml for improved security: pip install defusedxml"
    )

try:
    import requests
except ImportError:
    import urllib.error
    import urllib.request
    import warnings

    warnings.warn(
        "requests not available, using urllib. "
        "Install requests for improved security: pip install requests"
    )

from ..core.config import Config


def fetch_rss_data(rss_url: str, timeout: int = 30) -> Optional[str]:
    """Fetch RSS feed data from URL with error handling.

    Args:
        rss_url: URL of the RSS feed to fetch
        timeout: Request timeout in seconds

    Returns:
        Raw RSS XML content as string, or None if fetch fails

    Raises:
        Exception: If network request fails or other errors occur
    """
    logger = logging.getLogger(__name__)

    # Validate URL scheme for security
    if not rss_url.startswith(("https://", "http://")):
        logger.error(f"Invalid URL scheme, only HTTP/HTTPS allowed: {rss_url}")
        return None

    try:
        logger.debug(f"Fetching RSS data from {rss_url}")

        # Use requests if available for better security
        if "requests" in globals():
            response = requests.get(
                rss_url,
                timeout=timeout,
                headers={"User-Agent": "AWS-Services-Reporter/1.4.0"},
            )
            response.raise_for_status()
            data = response.text
        else:
            # Fallback to urllib with validation (URL scheme validated above)
            with urllib.request.urlopen(
                rss_url, timeout=timeout
            ) as response:  # nosec B310
                data = response.read().decode("utf-8")

        logger.info(f"Successfully fetched RSS data ({len(data)} bytes)")
        return data

    except Exception as e:
        logger.error(f"Failed to fetch RSS feed: {e}")
        return None


def extract_region_code_from_description(description: str) -> Optional[str]:
    """Extract AWS region code from RSS item description.

    Searches for region codes in various formats within the description text.

    Args:
        description: RSS item description text

    Returns:
        Region code (e.g., 'us-east-1') if found, None otherwise
    """
    # Common patterns for region codes in RSS descriptions
    patterns = [
        r"\b([a-z]{2}-[a-z]+-\d+)\b",  # Standard format: us-east-1, eu-west-1
        r"\b([a-z]{2}-[a-z]+[a-z]-\d+)\b",  # Extended format: ap-southeast-1
        r"region\s+([a-z]{2}-[a-z]+-\d+)",  # "region us-east-1"
        r"AWS\s+([a-z]{2}-[a-z]+-\d+)",  # "AWS us-east-1"
    ]

    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(1).lower()

    return None


def parse_rss_launch_dates(rss_data: str) -> Dict[str, Dict[str, str]]:
    """Parse RSS feed and extract region launch dates.

    Args:
        rss_data: Raw RSS XML content

    Returns:
        Dictionary mapping region codes to launch information:
        {
            'us-east-1': {
                'launch_date': '2006-08-25',
                'formatted_date': 'Fri, 25 Aug 2006',
                'announcement_title': 'US East (N. Virginia)',
                'announcement_url': 'https://...'
            }
        }

    Raises:
        ET.ParseError: If XML parsing fails
        Exception: For other parsing errors
    """
    logger = logging.getLogger(__name__)

    try:
        # defusedxml preferred, fallback has warning above for user awareness
        root = ET.fromstring(rss_data)  # nosec B314
        regions_data = {}

        # Find all RSS items
        items = root.findall(".//item")
        logger.info(f"Processing {len(items)} RSS items")

        for item in items:
            title_elem = item.find("title")
            description_elem = item.find("description")
            link_elem = item.find("link")
            pub_date_elem = item.find("pubDate")

            if title_elem is None or description_elem is None or pub_date_elem is None:
                continue

            title = title_elem.text or ""
            description = description_elem.text or ""
            link = link_elem.text or "" if link_elem is not None else ""
            pub_date = pub_date_elem.text or ""

            # Extract region code from description
            region_code = extract_region_code_from_description(description)
            if not region_code:
                # Try to extract from title as backup
                region_code = extract_region_code_from_description(title)

            if region_code:
                # Parse publication date
                try:
                    # RSS dates are typically in RFC 2822 format
                    # Example: "Fri, 25 Aug 2006 12:00:00 GMT"
                    parsed_date = datetime.strptime(
                        pub_date, "%a, %d %b %Y %H:%M:%S %Z"
                    )
                    iso_date = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    # Fallback for different date formats
                    try:
                        parsed_date = datetime.strptime(
                            pub_date, "%a, %d %b %Y %H:%M:%S %z"
                        )
                        iso_date = parsed_date.strftime("%Y-%m-%d")
                    except ValueError:
                        logger.warning(
                            f"Could not parse date '{pub_date}' for region {region_code}"
                        )
                        iso_date = "Unknown"

                regions_data[region_code] = {
                    "launch_date": iso_date,
                    "formatted_date": pub_date,
                    "announcement_title": title.strip(),
                    "announcement_url": link.strip(),
                }

                logger.debug(f"Parsed region {region_code}: {iso_date} - {title}")

        logger.info(f"Successfully parsed {len(regions_data)} regions from RSS feed")
        return regions_data

    except ET.ParseError as e:
        logger.error(f"Failed to parse RSS XML: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error parsing RSS data: {e}")
        raise


def get_rss_region_launch_dates(config: Config) -> Dict[str, Dict[str, str]]:
    """Fetch and parse AWS region launch dates from official RSS feed.

    Args:
        config: Configuration object (for potential future RSS URL customization)

    Returns:
        Dictionary mapping region codes to launch date information

    Raises:
        Exception: If RSS fetching or parsing fails completely
    """
    logger = logging.getLogger(__name__)

    # Official AWS regions RSS feed
    rss_url = (
        "https://docs.aws.amazon.com/global-infrastructure/latest/regions/regions.rss"
    )

    logger.info(f"Fetching AWS region launch dates from RSS feed")

    # Fetch RSS data
    rss_data = fetch_rss_data(rss_url)
    if not rss_data:
        logger.warning("Failed to fetch RSS data, returning empty results")
        return {}

    # Parse launch dates
    try:
        regions_data = parse_rss_launch_dates(rss_data)
        logger.info(
            f"Successfully extracted launch dates for {len(regions_data)} regions"
        )
        return regions_data
    except Exception as e:
        logger.error(f"Failed to parse RSS data: {e}")
        return {}


def merge_launch_date_sources(
    ssm_launch_date: str, rss_launch_data: Optional[Dict[str, str]]
) -> Dict[str, str]:
    """Merge launch date information from SSM and RSS sources.

    Prioritizes RSS feed data when available and valid, falls back to SSM data.

    Args:
        ssm_launch_date: Launch date from AWS SSM Parameter Store
        rss_launch_data: Launch date information from RSS feed (or None)

    Returns:
        Dictionary with merged launch date information:
        {
            'launch_date': '2006-08-25',
            'source': 'RSS' | 'SSM' | 'Unknown',
            'formatted_date': 'Fri, 25 Aug 2006',
            'announcement_url': 'https://...' (if from RSS)
        }
    """
    result = {
        "launch_date": "Unknown",
        "source": "Unknown",
        "formatted_date": "",
        "announcement_url": "",
    }

    # Prefer RSS data if available and valid
    if rss_launch_data and rss_launch_data.get("launch_date") != "Unknown":
        result.update(
            {
                "launch_date": rss_launch_data["launch_date"],
                "source": "RSS",
                "formatted_date": rss_launch_data.get("formatted_date", ""),
                "announcement_url": rss_launch_data.get("announcement_url", ""),
            }
        )
    # Fall back to SSM data
    elif ssm_launch_date and ssm_launch_date != "Unknown":
        result.update(
            {
                "launch_date": ssm_launch_date,
                "source": "SSM",
                "formatted_date": "",
                "announcement_url": "",
            }
        )

    return result
