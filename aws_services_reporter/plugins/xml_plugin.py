"""XML output plugin for AWS Services Reporter."""

import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.config import Config
from .base import BaseOutputPlugin


class XMLOutputPlugin(BaseOutputPlugin):
    """Plugin for generating XML output format."""

    name = "xml"
    description = "Generate XML format output with hierarchical structure"
    file_extension = "xml"
    requires_dependencies = []  # Uses built-in xml module

    def generate_output(
        self,
        config: Config,
        regions: Dict[str, Dict[str, Any]],
        region_services: Dict[str, List[str]],
        service_names: Optional[Dict[str, str]] = None,
        enhanced_services: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        quiet: bool = False,
    ) -> bool:
        """Generate XML output file.

        Args:
            config: Configuration object containing output settings
            regions: Dictionary mapping region codes to region details
            region_services: Dictionary mapping region codes to service lists
            service_names: Dictionary mapping service codes to display names
            enhanced_services: Dictionary with enhanced service metadata per region
            metadata: Optional metadata about the data fetch operation
            quiet: Suppress progress output if True

        Returns:
            True if XML file was successfully created, False otherwise
        """
        try:
            if not quiet:
                print("  📝 Creating XML output...")

            # Create root element
            root = ET.Element("aws_services_report")

            # Add metadata
            self._add_metadata(root, metadata)

            # Add summary statistics
            self._add_summary(root, regions, region_services, service_names)

            # Add regions data
            self._add_regions(root, regions, region_services, service_names)

            # Add services data
            self._add_services(root, region_services, service_names)

            # Create the tree and write to file
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)  # Pretty formatting

            output_path = self.get_output_path(
                config, Path(config.regions_filename).stem
            )

            tree.write(output_path, encoding="utf-8", xml_declaration=True)

            # Get file size for reporting
            file_size = output_path.stat().st_size

            if not quiet:
                print(f"    ✓ Created XML output ({file_size:,} bytes)")

            self.logger.info(f"Created XML output: {output_path} ({file_size:,} bytes)")
            return True

        except Exception as e:
            if not quiet:
                print(f"  ❌ Failed to create XML output: {e}")
            self.logger.error(f"Failed to create XML output: {e}")
            return False

    def _add_metadata(self, root: ET.Element, metadata: Optional[Dict[str, Any]]):
        """Add metadata section to XML.

        Args:
            root: Root XML element
            metadata: Metadata dictionary
        """
        meta_elem = ET.SubElement(root, "metadata")

        # Add generation timestamp
        ET.SubElement(meta_elem, "generated_at").text = datetime.utcnow().isoformat()

        # Add generator info
        generator = ET.SubElement(meta_elem, "generator")
        ET.SubElement(generator, "name").text = "AWS Services Reporter"
        ET.SubElement(generator, "version").text = "1.4.2"
        ET.SubElement(generator, "plugin").text = self.name

        # Add custom metadata if provided
        if metadata:
            custom_meta = ET.SubElement(meta_elem, "fetch_metadata")
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    ET.SubElement(custom_meta, key).text = str(value)

    def _add_summary(
        self,
        root: ET.Element,
        regions: Dict[str, Dict[str, Any]],
        region_services: Dict[str, List[str]],
        service_names: Optional[Dict[str, str]],
    ):
        """Add summary statistics to XML.

        Args:
            root: Root XML element
            regions: Dictionary mapping region codes to region details
            region_services: Dictionary mapping region codes to service lists
            service_names: Dictionary mapping service codes to display names
        """
        summary = ET.SubElement(root, "summary")

        # Calculate statistics
        all_services = set()
        for services in region_services.values():
            all_services.update(services)

        total_service_instances = sum(
            len(services) for services in region_services.values()
        )
        avg_services = total_service_instances / len(regions) if regions else 0

        # Add summary elements
        ET.SubElement(summary, "total_regions").text = str(len(regions))
        ET.SubElement(summary, "total_services").text = str(len(all_services))
        ET.SubElement(summary, "total_service_instances").text = str(
            total_service_instances
        )
        ET.SubElement(summary, "avg_services_per_region").text = f"{avg_services:.1f}"

        # Find most/least available services
        if all_services and region_services:
            service_counts = {}
            for service in all_services:
                count = sum(
                    1 for services in region_services.values() if service in services
                )
                service_counts[service] = count

            most_available = max(service_counts, key=service_counts.get)
            least_available = min(service_counts, key=service_counts.get)

            most_name = (
                service_names.get(most_available, most_available)
                if service_names
                else most_available
            )
            least_name = (
                service_names.get(least_available, least_available)
                if service_names
                else least_available
            )

            ET.SubElement(summary, "most_available_service").text = most_name
            ET.SubElement(summary, "least_available_service").text = least_name

    def _add_regions(
        self,
        root: ET.Element,
        regions: Dict[str, Dict[str, Any]],
        region_services: Dict[str, List[str]],
        service_names: Optional[Dict[str, str]],
    ):
        """Add regions section to XML.

        Args:
            root: Root XML element
            regions: Dictionary mapping region codes to region details
            region_services: Dictionary mapping region codes to service lists
            service_names: Dictionary mapping service codes to display names
        """
        regions_elem = ET.SubElement(root, "regions")

        for region_code in sorted(regions.keys()):
            region_details = regions[region_code]
            region_elem = ET.SubElement(regions_elem, "region")

            # Basic region info
            ET.SubElement(region_elem, "code").text = region_code
            ET.SubElement(region_elem, "name").text = region_details["name"]

            # Launch date info if available
            if "launch_date" in region_details:
                launch_info = ET.SubElement(region_elem, "launch_info")
                ET.SubElement(launch_info, "date").text = region_details["launch_date"]
                ET.SubElement(launch_info, "source").text = region_details.get(
                    "launch_date_source", "Unknown"
                )
                if region_details.get("announcement_url"):
                    ET.SubElement(launch_info, "announcement_url").text = (
                        region_details["announcement_url"]
                    )

            # Additional details
            if "az_count" in region_details:
                ET.SubElement(region_elem, "availability_zones").text = str(
                    region_details["az_count"]
                )
            if "partition" in region_details:
                ET.SubElement(region_elem, "partition").text = region_details[
                    "partition"
                ]

            # Services in this region
            services_elem = ET.SubElement(region_elem, "services")
            region_service_list = sorted(region_services.get(region_code, []))

            ET.SubElement(services_elem, "count").text = str(len(region_service_list))

            for service_code in region_service_list:
                service_elem = ET.SubElement(services_elem, "service")
                ET.SubElement(service_elem, "code").text = service_code
                service_name = (
                    service_names.get(service_code, service_code)
                    if service_names
                    else service_code
                )
                ET.SubElement(service_elem, "name").text = service_name

    def _add_services(
        self,
        root: ET.Element,
        region_services: Dict[str, List[str]],
        service_names: Optional[Dict[str, str]],
    ):
        """Add services section to XML.

        Args:
            root: Root XML element
            region_services: Dictionary mapping region codes to service lists
            service_names: Dictionary mapping service codes to display names
        """
        services_elem = ET.SubElement(root, "services")

        # Get all unique services
        all_services = set()
        for services in region_services.values():
            all_services.update(services)

        total_regions = len(region_services)

        for service_code in sorted(all_services):
            service_elem = ET.SubElement(services_elem, "service")

            # Basic service info
            ET.SubElement(service_elem, "code").text = service_code
            service_name = (
                service_names.get(service_code, service_code)
                if service_names
                else service_code
            )
            ET.SubElement(service_elem, "name").text = service_name

            # Availability info
            available_regions = [
                region
                for region, services in region_services.items()
                if service_code in services
            ]

            coverage_pct = (
                (len(available_regions) / total_regions) * 100
                if total_regions > 0
                else 0
            )

            availability = ET.SubElement(service_elem, "availability")
            ET.SubElement(availability, "region_count").text = str(
                len(available_regions)
            )
            ET.SubElement(availability, "coverage_percentage").text = (
                f"{coverage_pct:.1f}"
            )

            # List of regions where available
            regions_elem = ET.SubElement(availability, "regions")
            for region_code in sorted(available_regions):
                ET.SubElement(regions_elem, "region").text = region_code
