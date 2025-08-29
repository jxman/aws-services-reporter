"""AWS client modules for service data fetching.

Contains AWS API interactions, session management, and data fetching utilities.
"""

from .session import create_session
from .ssm_client import (
    get_all_parameters_by_path,
    get_all_regions_and_names,
    get_all_services,
    get_all_services_with_names,
    get_region_details,
    get_service_name,
    get_services_per_region,
    get_services_per_region_enhanced,
)

__all__ = [
    "create_session",
    "get_all_parameters_by_path",
    "get_region_details",
    "get_all_regions_and_names",
    "get_services_per_region",
    "get_services_per_region_enhanced",
    "get_all_services",
    "get_all_services_with_names",
    "get_service_name",
]
