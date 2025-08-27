"""Excel output generation for AWS Services Reporter.

Generates Excel workbooks with multiple formatted sheets containing regional service data.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.config import Config


def create_excel_output(
    config: Config,
    regions: Dict[str, str],
    region_services: Dict[str, List[str]],
    metadata: Optional[Dict[str, Any]] = None,
    quiet: bool = False,
) -> bool:
    """Generate Excel workbook with multiple formatted sheets.

    Args:
        config: Configuration object containing output settings
        regions: Dictionary mapping region codes to display names
        region_services: Dictionary mapping region codes to service lists
        metadata: Optional metadata about the data fetch operation
        quiet: Suppress progress output if True

    Returns:
        True if Excel file was successfully created, False if dependencies missing or error occurred

    Creates:
        Excel workbook (.xlsx) with multiple sheets:
        - Regional Services: List of regions and their services
        - Service Matrix: Services vs regions availability grid
        - Region Summary: Regions with service counts and names
        - Statistics: Summary data and metadata

    Requires:
        pandas and openpyxl packages for Excel functionality
    """
    output_path = (
        Path(config.output_dir) / "excel" / f"{Path(config.regions_filename).stem}.xlsx"
    )
    logger = logging.getLogger(__name__)

    try:
        import pandas as pd
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils.dataframe import dataframe_to_rows

        if not quiet:
            print(f"  📝 Creating Excel output...")

        # Prepare data for Excel sheets
        all_services = sorted(
            set().union(*region_services.values()) if region_services else []
        )

        # Create workbook
        wb = Workbook()

        # Remove default sheet
        wb.remove(wb.active)

        # Sheet 1: Regional Services
        ws_regional = wb.create_sheet("Regional Services")
        regional_data = []
        for region_code in sorted(regions.keys()):
            region_name = regions[region_code]
            services = sorted(region_services.get(region_code, []))
            for service in services:
                regional_data.append([region_code, region_name, service])

        # Add headers and data
        headers = ["Region Code", "Region Name", "Service Code"]
        ws_regional.append(headers)
        for row in regional_data:
            ws_regional.append(row)

        # Format headers
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(
            start_color="366092", end_color="366092", fill_type="solid"
        )
        for cell in ws_regional[1]:
            cell.font = header_font
            cell.fill = header_fill

        # Sheet 2: Service Matrix
        ws_matrix = wb.create_sheet("Service Matrix")
        sorted_regions = sorted(regions.keys())

        # Create matrix header
        matrix_header = ["Service"] + sorted_regions
        ws_matrix.append(matrix_header)

        # Create matrix data
        for service in all_services:
            row = [service]
            for region_code in sorted_regions:
                available = (
                    "✓" if service in region_services.get(region_code, []) else "✗"
                )
                row.append(available)
            ws_matrix.append(row)

        # Format matrix headers
        for cell in ws_matrix[1]:
            cell.font = header_font
            cell.fill = header_fill

        # Format availability indicators
        green_fill = PatternFill(
            start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"
        )
        red_fill = PatternFill(
            start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"
        )

        for row in ws_matrix.iter_rows(min_row=2):
            for cell in row[1:]:  # Skip service name column
                if cell.value == "✓":
                    cell.fill = green_fill
                elif cell.value == "✗":
                    cell.fill = red_fill

        # Sheet 3: Region Summary
        ws_summary = wb.create_sheet("Region Summary")

        # Create region summary data
        summary_data = []
        for region_code in sorted(regions.keys()):
            region_name = regions[region_code]
            service_count = len(region_services.get(region_code, []))
            summary_data.append([region_code, region_name, service_count])

        # Add headers and data
        summary_headers = ["Region Code", "Region Name", "Service Count"]
        ws_summary.append(summary_headers)
        for row in summary_data:
            ws_summary.append(row)

        # Format summary headers
        for cell in ws_summary[1]:
            cell.font = header_font
            cell.fill = header_fill

        # Format service count column with number formatting
        for row_idx in range(2, len(summary_data) + 2):
            cell = ws_summary.cell(row=row_idx, column=3)
            cell.alignment = Alignment(horizontal="right")

        # Sheet 4: Statistics
        ws_stats = wb.create_sheet("Statistics")

        # Calculate statistics
        total_service_instances = sum(
            len(services) for services in region_services.values()
        )
        avg_services = total_service_instances / len(regions) if regions else 0

        # Most/least available services
        service_coverage = {}
        for service in all_services:
            available_regions = [
                region
                for region, services in region_services.items()
                if service in services
            ]
            service_coverage[service] = len(available_regions)

        most_available = (
            max(service_coverage.keys(), key=lambda x: service_coverage[x])
            if service_coverage
            else "N/A"
        )
        least_available = (
            min(service_coverage.keys(), key=lambda x: service_coverage[x])
            if service_coverage
            else "N/A"
        )

        # Add statistics data
        stats_data = [
            ["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Generator", "AWS Services Reporter v1.3.0"],
            [""],
            ["Summary Statistics", ""],
            ["Total Regions", len(regions)],
            ["Total Services", len(all_services)],
            ["Total Service Instances", total_service_instances],
            ["Average Services per Region", f"{avg_services:.1f}"],
            [
                "Most Available Service",
                f"{most_available} ({service_coverage.get(most_available, 0)} regions)",
            ],
            [
                "Least Available Service",
                f"{least_available} ({service_coverage.get(least_available, 0)} regions)",
            ],
        ]

        if metadata:
            stats_data.extend(
                [
                    [""],
                    ["Fetch Metadata", ""],
                    ["Fetch Duration (seconds)", metadata.get("fetch_duration", "N/A")],
                    ["AWS Profile", metadata.get("aws_profile", "default")],
                ]
            )

        for row_data in stats_data:
            ws_stats.append(row_data)

        # Format statistics sheet
        for row in ws_stats.iter_rows():
            if row[0].value in ["Summary Statistics", "Fetch Metadata"]:
                for cell in row:
                    cell.font = Font(bold=True, size=12)
                    cell.fill = PatternFill(
                        start_color="D9D9D9", end_color="D9D9D9", fill_type="solid"
                    )

        # Auto-adjust column widths
        for ws in [ws_regional, ws_matrix, ws_summary, ws_stats]:
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save workbook
        wb.save(output_path)

        # Get file size for both display and logging
        file_size = output_path.stat().st_size

        if not quiet:
            print(
                f"    ✓ Created Excel output ({file_size:,} bytes, {len(wb.worksheets)} sheets)"
            )

        logger.info(f"Created Excel output: {output_path} ({file_size:,} bytes)")
        return True

    except ImportError as e:
        if not quiet:
            print(f"  ⚠️  Excel output requires pandas and openpyxl: {e}")
        logger.warning(f"Excel output dependencies missing: {e}")
        return False
    except Exception as e:
        if not quiet:
            print(f"  ❌ Failed to create Excel output: {e}")
        logger.error(f"Failed to create Excel output: {e}")
        return False
