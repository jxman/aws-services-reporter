#!/usr/bin/env python3
"""AWS Services Reporter - Main application entry point.

Orchestrates the complete data fetching, processing, and output generation workflow
using a modular architecture for maintainability and extensibility.

This refactored version uses the new modular structure for better code organization.
"""

import time
from pathlib import Path

from aws_services_reporter.aws_client.session import create_session
from aws_services_reporter.aws_client.ssm_client import (
    get_all_regions_and_names,
    get_all_services_with_names,
    get_services_per_region,
    get_services_per_region_enhanced,
)
from aws_services_reporter.core.cache import AWSDataCache

# Import from our modular structure
from aws_services_reporter.core.config import create_config_from_args, setup_logging
from aws_services_reporter.core.progress import ProgressTracker
from aws_services_reporter.output.csv_output import (
    create_region_summary_csv,
    create_regions_services_csv,
    create_service_summary_csv,
    create_services_regions_matrix_csv,
)
from aws_services_reporter.output.excel_output import create_excel_output
from aws_services_reporter.output.json_output import create_json_output
from aws_services_reporter.utils.cli import (
    parse_arguments,
    show_cache_help,
    show_examples,
)


def main() -> None:
    """Main entry point for AWS Services Reporter application.

    Orchestrates the complete data fetching, processing, and output generation workflow.
    Handles command-line arguments, configuration, caching, progress tracking, and
    multiple output formats with comprehensive error handling.

    Workflow:
        1. Parse command-line arguments and create configuration
        2. Setup logging and progress tracking
        3. Handle special commands (help, cache operations)
        4. Check for cached data or fetch fresh data from AWS
        5. Generate requested output formats (CSV, JSON, Excel)
        6. Display performance statistics and completion status

    Raises:
        SystemExit: For help commands or critical errors
        Exception: For unrecoverable errors during execution
    """
    # Parse command-line arguments
    args = parse_arguments()
    config = create_config_from_args(args)

    # Setup logging
    logger = setup_logging(config.log_level)
    quiet = getattr(args, "quiet", False)

    # Initialize progress tracker
    progress = ProgressTracker(use_rich=config.use_rich, quiet=quiet)

    # Initialize cache system
    cache = AWSDataCache(
        cache_file=str(Path(config.output_dir) / config.cache_file),
        cache_hours=config.cache_hours,
    )

    # Handle special commands
    if getattr(args, "examples", False):
        show_examples()
        return

    if getattr(args, "cache_help", False):
        show_cache_help()
        return

    if getattr(args, "cache_stats", False):
        stats = cache.get_stats()
        progress.print_panel(
            f"""Cache Statistics:
• Exists: {'✓' if stats.get('exists') else '✗'}
• Valid: {'✓' if stats.get('valid') else '✗'}
• Age: {stats.get('age_hours', 0):.1f} hours
• Size: {stats.get('file_size', 0):,} bytes
• Regions: {stats.get('cache_info', {}).get('total_regions', 'N/A')}
• Services: {stats.get('cache_info', {}).get('total_services', 'N/A')}
• Updated: {stats.get('timestamp', 'N/A')}""",
            "🔄 Cache Information",
        )
        return

    if getattr(args, "clear_cache", False):
        if cache.clear():
            progress.print_status("✅ Cache cleared successfully", "green")
        else:
            progress.print_status("❌ Failed to clear cache", "red")
        return

    start_time = time.time()

    try:
        # Check cache first
        if config.cache_enabled:
            progress.print_status("🔍 Checking cache...", "blue")
            cached_data = cache.load()
            if cached_data:
                progress.print_status("✅ Using cached data", "green")
                regions = cached_data["regions"]
                region_services = cached_data["region_services"]
                service_names = cached_data.get("service_names", {})
                enhanced_services = cached_data.get("enhanced_services", {})
                metadata = cached_data.get("metadata", {})
            else:
                progress.print_status("⏳ Cache miss - fetching fresh data", "yellow")
                cached_data = None
        else:
            progress.print_status("⏳ Cache disabled - fetching fresh data", "yellow")
            cached_data = None

        # Fetch fresh data if no valid cache
        if not cached_data:
            session = create_session(config)

            # Fetch regions, services, and service names
            regions = get_all_regions_and_names(config, session, quiet)
            region_services = get_services_per_region(config, session, quiet)
            service_names = get_all_services_with_names(config, session, quiet)

            # Conditionally fetch enhanced metadata
            if config.enhanced_metadata:
                enhanced_services = get_services_per_region_enhanced(
                    config, session, quiet
                )
            else:
                if not quiet:
                    print("⚡ Skipping enhanced metadata for faster execution")
                enhanced_services = {}

            fetch_duration = time.time() - start_time
            metadata = {
                "fetch_duration": round(fetch_duration, 2),
                "aws_profile": config.aws_profile,
                "aws_region": config.aws_region,
                "cache_enabled": config.cache_enabled,
            }

            # Save to cache if enabled
            if config.cache_enabled:
                if cache.save(
                    regions,
                    region_services,
                    service_names,
                    enhanced_services,
                    metadata,
                ):
                    progress.print_status("💾 Data cached for future runs", "green")

        # Generate outputs
        if not quiet:
            print("\n📊 Generating outputs...")
            unique_services = len(set().union(*region_services.values()))
            print(
                f"   Found {len(regions)} regions with {unique_services} unique services"
            )

        output_success = []

        # Generate requested formats
        for format_type in config.output_formats:
            if format_type == "csv":
                create_regions_services_csv(
                    config,
                    regions,
                    region_services,
                    service_names,
                    enhanced_services,
                    quiet,
                )
                create_services_regions_matrix_csv(
                    config, regions, region_services, service_names, quiet
                )
                output_success.append("CSV")

            elif format_type == "json":
                if create_json_output(
                    config,
                    regions,
                    region_services,
                    service_names,
                    enhanced_services,
                    metadata,
                    quiet,
                ):
                    output_success.append("JSON")

            elif format_type == "excel":
                if create_excel_output(
                    config,
                    regions,
                    region_services,
                    service_names,
                    enhanced_services,
                    metadata,
                    quiet,
                ):
                    output_success.append("Excel")

            elif format_type == "region-summary":
                create_region_summary_csv(config, regions, region_services, quiet)
                output_success.append("Region Summary")

            elif format_type == "service-summary":
                create_service_summary_csv(
                    config, regions, region_services, service_names, quiet
                )
                output_success.append("Service Summary")

        # Show completion summary
        total_time = time.time() - start_time

        if not quiet:
            progress.print_panel(
                f"""✅ Report Generation Complete!

📊 Data Summary:
• Regions: {len(regions):,}
• Services: {len(set().union(*region_services.values())):,}
• Service Instances: {sum(len(services) for services in region_services.values()):,}

📁 Generated Outputs:
• {', '.join(output_success)}

⏱️  Performance:
• Total Time: {total_time:.1f} seconds
• Cache Used: {'✅' if cached_data else '❌'}
• Data Source: {'Cache' if cached_data else 'AWS API'}

💡 Next Steps:
• View generated files in: {config.output_dir}
• Use --cache-stats to monitor cache health
• Try --format json excel for more output formats""",
                "🚀 AWS Services Reporter",
            )

        logger.info(f"Report generation completed in {total_time:.1f} seconds")

    except KeyboardInterrupt:
        progress.print_status("\n⚠️  Operation interrupted by user", "yellow")
        logger.info("Operation interrupted by user")
    except Exception as e:
        progress.print_status(f"❌ Error: {e}", "red")
        logger.error(f"Application error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
