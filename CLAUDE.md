# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This high-performance Python project generates comprehensive reports of AWS services availability across all regions using AWS Systems Manager (SSM) Parameter Store. Features intelligent caching (99% time savings), modular architecture, multiple output formats, and professional progress tracking.

**Current Version: v1.4.0 (RSS Integration Complete - Enhanced Launch Dates)**

## 🏗️ Project Architecture

### Modular Structure (v1.4.0+)
```
aws-services/
├── aws_services_reporter/          # Main package (modular architecture)
│   ├── core/                      # Core functionality
│   │   ├── config.py              # Configuration & argument processing
│   │   ├── cache.py               # Intelligent caching system
│   │   └── progress.py            # Rich UI & progress tracking
│   ├── aws_client/               # AWS API interactions
│   │   ├── session.py            # Session & credential management
│   │   ├── ssm_client.py         # SSM Parameter Store client
│   │   └── rss_client.py         # RSS feed parser for launch dates
│   ├── output/                   # Report generation
│   │   ├── csv_output.py         # CSV reports
│   │   ├── json_output.py        # JSON with statistics
│   │   └── excel_output.py       # Excel with multiple sheets
│   └── utils/                    # Utilities & CLI
│       └── cli.py                # Command-line interface
├── reports/                      # Generated reports (organized)
│   ├── csv/                      # CSV outputs
│   ├── json/                     # JSON outputs  
│   ├── excel/                    # Excel outputs
│   └── cache/                    # Cache files
├── tests/                        # Comprehensive test suite
│   ├── test_cache.py             # Cache system tests
│   ├── test_aws_integration.py   # AWS API mocking tests
│   ├── test_configuration.py     # Config & CLI tests
│   ├── test_output_formats.py    # Output generation tests
│   └── test_rss_client.py        # RSS feed integration tests
├── .github/workflows/            # CI/CD pipeline
├── main.py                       # Application entry point (193 lines)
├── .gitignore                    # Comprehensive Python + project patterns
└── requirements.txt              # Runtime dependencies
```

### Key Design Principles
- **Single Responsibility**: Each module has a clear, focused purpose
- **Loose Coupling**: Modules interact through well-defined interfaces
- **High Cohesion**: Related functionality grouped together
- **Type Safety**: Comprehensive type hints (85%+ coverage)
- **Documentation**: Extensive docstrings and inline documentation
- **Clean Organization**: Organized file structure with comprehensive .gitignore
- **Professional Standards**: Production-ready code with proper error handling

## Key Features

### 🔄 **Intelligent Caching System**
- **99% time savings** on subsequent runs (90 seconds → 5 seconds)
- Automatic cache validation with configurable TTL (default: 24 hours)
- Smart cache management with statistics and manual controls
- Cache location: `reports/cache/aws_data_cache.json` (~150-200KB)

### 📡 **RSS Feed Integration (New in v1.4.0)**
- **Enhanced launch dates** from official AWS documentation RSS feed
- **87% coverage**: 33 of 38 regions with precise launch dates
- **Data source prioritization**: RSS → SSM → Unknown with visual indicators
- **Rich metadata**: Announcement URLs, formatted dates, and data source tracking
- **Intelligent merging**: Combines RSS and SSM data for comprehensive coverage

### 📊 **Multiple Output Formats**
- **CSV**: Traditional spreadsheet format (in `reports/csv/`)
- **JSON**: Rich data with statistics and metadata (in `reports/json/`)
- **Excel**: Multi-sheet workbook with formatting (in `reports/excel/`) - 4 sheets including Region Summary
- **Region Summary**: Dedicated CSV report with region codes, names, and service counts

### ⚡ **Performance Optimizations**
- **Concurrent processing**: 10 concurrent API calls by default
- **Exponential backoff**: Smart retry logic for rate limiting
- **Connection pooling**: Reuses HTTP connections efficiently
- **Memory optimization**: Streams large datasets

### 🎯 **Rich User Interface**
- **Progress tracking**: Beautiful progress bars and spinners (Rich library)
- **Status panels**: Professional completion summaries
- **Graceful fallbacks**: Works without Rich library

## Development Setup

### Environment Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt      # Runtime dependencies
pip install -r requirements-dev.txt  # Development dependencies (testing, linting)
```

### Key Commands
```bash
# Basic usage
python main.py                       # Generate CSV reports (default)
python main.py --format json excel   # Multiple formats
python main.py --format region-summary # Region summary only
python main.py --examples            # Show usage examples
python main.py --cache-stats          # View cache information

# Development
python -m pytest tests/ -v --cov     # Run tests with coverage
mypy main.py --ignore-missing-imports # Type checking
black . && isort . && flake8 .       # Code formatting & linting
```

### File Locations (Updated for v1.3.0)
- **Reports**: `reports/` directory (organized by type)
- **Cache**: `reports/cache/aws_data_cache.json`
- **Logs**: `reports/aws_services.log`
- **Tests**: `tests/` directory
- **Config**: Default output to `reports/` (configurable)

## Development Guidelines

### Code Style & Quality
- **Type hints**: Required for all functions and methods
- **Docstrings**: Google style with Args, Returns, Raises sections  
- **Error handling**: Comprehensive exception handling with logging
- **Testing**: Aim for 80%+ test coverage
- **Formatting**: Use black, isort, and flake8

### Module Guidelines
- **Size**: Keep modules under 200 lines when possible
- **Dependencies**: Minimize inter-module dependencies
- **Imports**: Use absolute imports from package root
- **Testing**: Each module should have corresponding test file
- **Documentation**: Every public function needs docstring

### Performance Considerations
- **Caching**: Always check cache before API calls
- **Concurrency**: Use ThreadPoolExecutor for I/O-bound operations
- **Memory**: Stream large data sets, avoid loading everything into memory
- **Rate Limiting**: Implement exponential backoff for AWS APIs

## Testing Strategy

### Test Structure
```bash
tests/
├── test_cache.py             # Cache system (TTL, corruption, stats)
├── test_aws_integration.py   # AWS API calls with moto mocking
├── test_configuration.py     # Config management and CLI parsing  
├── test_output_formats.py    # CSV, JSON, Excel generation
```

### Key Test Patterns
- **Mocking**: Use `moto` for AWS service mocking
- **Fixtures**: Create reusable test data in `conftest.py`
- **Coverage**: Aim for edge cases and error conditions
- **Integration**: Test end-to-end workflows

### Running Tests
```bash
# All tests with coverage
python -m pytest tests/ -v --cov=aws_services_reporter --cov-report=term-missing

# Specific test categories  
python -m pytest tests/test_cache.py -v
python -m pytest tests/test_aws_integration.py -v

# Generate coverage report
python -m pytest tests/ --cov=aws_services_reporter --cov-report=html
```

## Common Tasks

### Adding New Output Format
1. Create new module in `aws_services_reporter/output/`
2. Implement format-specific generation function
3. Add to CLI choices in `utils/cli.py`
4. Update main.py format handling logic
5. Add comprehensive tests
6. Update documentation

### Adding New Configuration Option
1. Add to `Config` dataclass in `core/config.py`
2. Add CLI argument in `utils/cli.py`
3. Update `create_config_from_args` function
4. Add validation if needed
5. Update documentation and examples

### Performance Optimization
1. Profile with `python -m cProfile main.py`
2. Focus on I/O-bound operations (API calls)
3. Consider increasing `--max-workers` for faster systems
4. Monitor cache hit rates with `--cache-stats`
5. Use `--log-level DEBUG` for detailed timing

## Architecture Evolution

### Version History
- **v1.0**: Single script (~600 lines)
- **v1.1**: Added concurrency (~800 lines)  
- **v1.2**: Intelligent caching (~1,200 lines)
- **v1.3**: Modular architecture (distributed across focused modules)
- **v1.4**: RSS feed integration for enhanced launch dates with comprehensive testing

### Design Decisions
- **SSM Parameter Store**: Chosen for comprehensive service data
- **ThreadPoolExecutor**: Optimal for I/O-bound AWS API calls
- **Rich Library**: Professional terminal UI without complexity
- **Modular Architecture**: Supports testing, maintenance, and extensibility

## Troubleshooting

### Common Issues
- **Import errors**: Check virtual environment activation
- **AWS credentials**: Verify `aws configure` or IAM roles
- **Cache corruption**: Use `python main.py --clear-cache`
- **Rate limiting**: Reduce `--max-workers` or increase `--max-retries`
- **Permission errors**: Check output directory write permissions

### Debug Commands
```bash
python main.py --log-level DEBUG     # Detailed logging
python main.py --cache-stats          # Cache diagnostics
python main.py --no-cache --quiet    # Force fresh data
```

## Next Development Priorities

### Phase 4A (v1.5.0) - In Progress
- **Plugin system**: Extensible output formats
- **Advanced CLI**: Service filtering, custom regions
- **API documentation**: Sphinx-generated docs
- **Enhanced RSS features**: Custom RSS URLs, historical analysis

### Performance Targets
- **Maintain <5s cached runs**
- **<90s fresh data runs**
- **Memory usage <100MB**
- **Test coverage >80%**

---

**Last Updated**: August 30, 2024  
**Architecture**: Modular with RSS Integration (v1.4.0)  
**Next Milestone**: Plugin System (v1.5.0)
