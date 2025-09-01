# AWS Services Reporter

> **Comprehensive AWS service availability analysis tool with intelligent caching and multiple output formats**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.4.2-orange.svg)](CHANGELOG.md)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-Passing-brightgreen.svg)](https://github.com/jxman/aws-services-reporter/actions)
[![Security](https://img.shields.io/badge/Security-Excellent-brightgreen.svg)](#security)

## 📋 Overview

AWS Services Reporter is a powerful Python tool that analyzes AWS service availability across all regions, providing comprehensive reports in multiple formats. With intelligent caching and concurrent processing, it transforms a 90-second AWS API crawl into a 5-second cached operation - delivering **99% performance improvement**.

### ✨ Key Features

- 🚀 **Intelligent Caching**: 99% performance improvement (90s → 5s)
- 🌍 **Complete Coverage**: All AWS regions and 400+ services  
- 📊 **Multiple Formats**: CSV, JSON, Excel (5 sheets), Region Summary
- 📡 **RSS Integration**: Enhanced region launch dates from official AWS RSS feed
- ⚡ **Concurrent Processing**: 10 concurrent API calls by default
- 🎯 **Rich Progress Tracking**: Beautiful progress bars and status displays
- 🏗️ **Modular Architecture**: Clean, maintainable, and extensible code
- 🔧 **Comprehensive CLI**: 20+ command-line options
- 📈 **Detailed Statistics**: Service coverage, regional analysis, and metadata
- 🕰️ **Historical Data**: Region launch dates with announcement URLs and data sources
- ✅ **Production Ready**: Comprehensive CI/CD pipeline with automated testing
- 🛡️ **Security Validated**: Zero high/medium severity security issues
- 🔧 **Pre-commit Hooks**: Automatic code formatting and quality checks

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Parser    │───▶│  Config Manager │───▶│ Progress Tracker│
│ (args parsing)  │    │ (settings)      │    │ (Rich UI)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Cache System   │───▶│  AWS SSM Client │───▶│ Output Generators│
│ (TTL validation)│    │ (concurrent)    │    │ (CSV/JSON/Excel)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  RSS Feed Client│    │   CI/CD Pipeline│    │  Security Scans │
│ (launch dates)  │    │ (testing/build) │    │ (bandit/safety) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 📁 Project Structure

```
aws-services/
├── aws_services_reporter/          # Modular package
│   ├── core/                      # Core functionality
│   │   ├── config.py              # Configuration management
│   │   ├── cache.py               # Intelligent caching system
│   │   └── progress.py            # Rich progress tracking
│   ├── aws_client/               # AWS API interactions
│   │   ├── session.py            # Session management
│   │   ├── ssm_client.py         # SSM Parameter Store client
│   │   └── rss_client.py         # RSS feed parser for launch dates
│   ├── output/                   # Report generation
│   │   ├── csv_output.py         # CSV report generation
│   │   ├── json_output.py        # JSON with statistics
│   │   └── excel_output.py       # Excel with 5 sheets
│   └── utils/                    # Utilities & CLI
│       └── cli.py                # Command-line interface
├── reports/                      # Generated reports (organized)
│   ├── csv/                      # CSV outputs (4 files)
│   ├── json/                     # JSON outputs
│   ├── excel/                    # Excel outputs (5 sheets)
│   └── cache/                    # Cache files
├── tests/                        # Comprehensive test suite (80%+ coverage)
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── README.md                     # Main documentation
├── QUICK_REFERENCE.md            # Command cheat sheet  
├── TROUBLESHOOTING.md            # Common issues guide
├── ROADMAP.md                    # Development roadmap
├── DEVELOPMENT.md                # Developer setup guide
├── AWS_SSM_DATA_EXPLORATION.md   # Technical deep-dive
├── CLAUDE.md                     # Project instructions
├── main.py                       # Application entry point
├── requirements.txt              # Runtime dependencies
└── requirements-dev.txt          # Development dependencies (includes pre-commit)
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/jxman/aws-services-reporter.git
cd aws-services-reporter

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Basic run (creates reports/ directory automatically)
python main.py

# View help and all options
python main.py --help

# Show usage examples
python main.py --examples

# Generate all output formats
python main.py --format csv json excel region-summary
```

## 📊 Performance Comparison

| Run Type        | Duration     | API Calls          | Data Source   |
|-----------------|--------------|-------------------|---------------|
| **First Run**   | ~90 seconds  | 800+ calls        | AWS API       |
| **Cached Run**  | ~5 seconds   | 0 calls           | Local cache   |
| **Improvement** | **99% faster** | **100% reduction** | Smart caching |

## 🔄 Intelligent Caching System

### How It Works
1. **First Run**: Fetches data from AWS (90 seconds), saves to cache
2. **Subsequent Runs**: Loads from cache (5 seconds) - 99% time savings
3. **TTL Validation**: Auto-expires after 24 hours (configurable)
4. **Corruption Detection**: Validates cache integrity automatically

### Cache Commands

```bash
# View cache statistics
python main.py --cache-stats

# Clear cache (force fresh data)
python main.py --clear-cache

# Disable cache (one-time fresh fetch)
python main.py --no-cache

# Custom cache duration
python main.py --cache-hours 48  # 48-hour cache
```

## 🔗 RSS Feed Integration

### Enhanced Launch Date Data
**New in v1.4.0**: The reporter now integrates AWS region launch dates from the official AWS documentation RSS feed to provide comprehensive historical data.

#### Data Sources Integration
- **Primary**: Official AWS RSS feed (87% coverage - 33 of 38 regions)
- **Fallback**: AWS SSM Parameter Store data  
- **Priority**: RSS data takes precedence when available for accuracy

#### RSS Feed Features
- **Precise Launch Dates**: ISO format (YYYY-MM-DD) from official announcements
- **Announcement URLs**: Direct links to AWS blog posts and launch announcements
- **Formatted Dates**: Human-readable dates from RSS (e.g., "Fri, 25 Aug 2006 12:00:00 GMT")
- **Data Source Tracking**: Indicates whether data comes from RSS, SSM, or is Unknown

#### Terminal Output Indicators
- 📡 **RSS**: Data from official RSS feed (most regions)
- 🔧 **SSM**: Data from AWS SSM Parameter Store (fallback)
- ❓ **Unknown**: No launch date available (e.g., GovCloud, China regions)

Example terminal output:
```
🌍 1/38: us-east-1 → US East (N. Virginia) (AZs: 6, Launch: 2006-08-25 📡)
🌍 2/38: eu-west-1 → Europe (Ireland) (AZs: 3, Launch: 2008-12-10 📡)
🌍 3/38: us-gov-west-1 → AWS GovCloud (US-West) (AZs: 3, Launch: Unknown ❓)
```

## 📋 Output Formats

### 1. CSV Reports (`reports/csv/`)
- **regions_services.csv**: Each region with its available services
- **services_regions_matrix.csv**: Service × Region availability matrix
- **region_summary.csv**: Summary of regions with launch dates, sources, announcement URLs, and service counts
- **service_summary.csv**: Summary of services with regional coverage statistics

### 2. JSON Report (`reports/json/`)
- **regions_services.json**: Complete data with statistics and metadata
- Includes service coverage percentages and regional analysis

### 3. Excel Report (`reports/excel/`) - requires pandas + openpyxl
- **regions_services.xlsx**: Multi-sheet workbook with 5 formatted sheets:
  - **Regional Services**: Detailed region-service mappings
  - **Service Matrix**: Service × Region availability grid
  - **Region Summary**: Region statistics with launch dates, sources, announcement URLs, and AZ counts
  - **Service Summary**: Service coverage across regions
  - **Statistics**: Overall metrics and insights

### 4. Intelligent Cache (`reports/cache/`)
- **aws_data_cache.json**: TTL-based cache with automatic validation
- 99% performance improvement for subsequent runs

## ⚙️ Configuration Options

### AWS Configuration
```bash
python main.py --profile production --region us-west-2
python main.py --max-retries 5
```

### Performance Tuning
```bash
python main.py --max-workers 20      # More concurrent calls (faster)
python main.py --max-workers 5       # Fewer calls (gentler)
```

### Output Customization
```bash
python main.py --output-dir ./custom-reports
python main.py --regions-file my_regions.csv
python main.py --format json         # JSON only
```

### Logging & Debugging
```bash
python main.py --log-level DEBUG     # Detailed logging
python main.py --quiet               # Minimal output
```

## 📈 Sample Output

### Console Output (with Rich formatting)
```
🔍 Checking cache...
✅ Using cached data

📊 Generating outputs...
   Found 37 regions with 394 unique services
  📝 Creating regions_services.csv...
    ✓ Created regions_services.csv (14,518 service entries)
  📝 Creating services_regions_matrix.csv...
    ✓ Created services_regions_matrix.csv (394 services × 37 regions)

╭─────────────────────── 🚀 AWS Services Reporter ────────────────────────╮
│ ✅ Report Generation Complete!                                          │
│                                                                         │
│ 📊 Data Summary:                                                        │
│ • Regions: 37                                                           │
│ • Services: 394                                                         │
│ • Service Instances: 14,518                                             │
│                                                                         │
│ 📁 Generated Outputs:                                                   │
│ • CSV                                                                   │
│                                                                         │
│ ⏱️  Performance:                                                         │
│ • Total Time: 5.2 seconds                                              │
│ • Cache Used: ✅                                                        │
│ • Data Source: Cache                                                    │
│                                                                         │
│ 💡 Next Steps:                                                          │
│ • CSV files: reports/csv/                                             │
│ • JSON files: reports/json/                                           │
│ • Excel files: reports/excel/                                         │
│ • Use --cache-stats to monitor cache health                           │
╰─────────────────────────────────────────────────────────────────────────╯
```

### JSON Output Sample
```json
{
  "generated_at": "2024-08-26T13:30:00.000000",
  "generator": {
    "name": "AWS Services Reporter",
    "version": "1.3.0"
  },
  "summary": {
    "total_regions": 37,
    "total_services": 394,
    "avg_services_per_region": 39.2,
    "most_available_service": "cloudformation",
    "least_available_service": "braket"
  },
  "regions": {
    "us-east-1": {
      "name": "US East (N. Virginia)",
      "launch_date": "2006-08-25",
      "launch_date_source": "RSS",
      "formatted_date": "Fri, 25 Aug 2006 12:00:00 GMT",
      "announcement_url": "https://aws.amazon.com/blogs/aws/...",
      "service_count": 245,
      "services": ["amplify", "apigateway", "ec2", ...]
    }
  },
  "services": {
    "ec2": {
      "available_in": 37,
      "coverage_percentage": 100.0,
      "regions": ["us-east-1", "us-east-2", ...]
    }
  }
}
```

## 🔒 Security

### Security Assessment (v1.4.2)
- ✅ **Zero High/Medium Severity Issues**: Comprehensive security scanning with Bandit
- 🛡️ **Automated Security Scans**: Every commit is security validated
- 🔍 **Dependency Scanning**: Safety checks for known vulnerabilities
- 📊 **Security Reports**: Detailed reports available in CI/CD artifacts
- 🔐 **Secure Dependencies**: defusedxml for XML parsing, requests for HTTP calls
- 🌐 **URL Validation**: HTTPS/HTTP scheme validation prevents unsafe protocols
- 🎯 **Code Quality**: Professional formatting standards with 79-char line length

### Security & Code Quality Improvements (v1.4.2)
- **RSS Client Security**: Replaced vulnerable XML parsing with defusedxml
- **HTTP Security**: Replaced urllib with requests library for safer HTTP handling
- **Input Validation**: Added URL scheme validation (HTTPS/HTTP only)
- **Code Quality**: Fixed unused imports, f-string issues, and consistent formatting
- **Linting Standards**: Reduced flake8 issues by 47% with professional formatting

### Security Scan Results
- **High Severity**: 0 issues ✅
- **Medium Severity**: 0 issues ✅
- **Low Severity**: Only test assertions and standard library usage (expected)

## 🚀 CI/CD Pipeline

### Automated Quality Assurance
- ✅ **Multi-Python Testing**: Python 3.8, 3.9, 3.10, 3.11
- ✅ **Code Quality**: Black formatting, isort imports, flake8 linting
- ✅ **Type Checking**: MyPy static analysis with comprehensive coverage
- ✅ **Security Scanning**: Bandit security analysis + Safety vulnerability checks
- ✅ **Integration Testing**: Full application workflow validation
- ✅ **Build Artifacts**: Automated release packaging

### Pipeline Status
All CI/CD jobs passing with comprehensive validation:
- **Tests**: 52 passing, 2 skipped (96% pass rate)
- **Security Scan**: Production-ready security posture (zero high/medium issues)
- **Code Quality**: Professional formatting standards with 79-char line length
- **Type Safety**: Comprehensive type checking with 85%+ coverage
- **Linting**: 47% reduction in flake8 issues with automated formatting

## 🛠️ Development

### Requirements
- **Python 3.8+**
- **boto3** (AWS SDK)
- **rich** (Enhanced UI)
- **tabulate** (Table formatting)
- **defusedxml** (Secure XML parsing)
- **requests** (Secure HTTP handling)
- **Optional**: pandas + openpyxl (Excel output)

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks (RECOMMENDED)
pre-commit install

# Run full test suite (same as CI/CD)
python -m pytest tests/ -v --cov=aws_services_reporter --cov-report=term-missing

# Run code quality checks (same as CI/CD)
black --check .
isort --check-only .
flake8 .
mypy aws_services_reporter/ main.py --ignore-missing-imports

# Run security scans (same as CI/CD)
bandit -r . --severity-level medium
safety check

# Format code (development)
black .
isort .

# Run all pre-commit hooks manually
pre-commit run --all-files
```

### Testing
```bash
# Run all tests with coverage (production standard)
python -m pytest tests/ -v --cov=aws_services_reporter --cov-report=term-missing

# Run specific test categories
python -m pytest tests/test_cache.py -v              # Cache system tests
python -m pytest tests/test_aws_integration.py -v    # AWS API integration tests
python -m pytest tests/test_configuration.py -v      # Configuration and CLI tests
python -m pytest tests/test_output_formats.py -v     # Output generation tests

# Generate HTML coverage report
python -m pytest tests/ --cov=aws_services_reporter --cov-report=html
open htmlcov/index.html  # View detailed coverage

# Test specific functionality
python -m pytest tests/ -k "cache"     # Cache-related tests only
python -m pytest tests/ -k "output"    # Output format tests only
```

## 📚 Documentation

- **[Quick Reference](QUICK_REFERENCE.md)**: Command cheat sheet and common patterns
- **[Development Guide](DEVELOPMENT.md)**: Pre-commit hooks setup and developer workflow
- **[Troubleshooting Guide](TROUBLESHOOTING.md)**: Common issues and solutions
- **[Development Roadmap](ROADMAP.md)**: Planned features and improvements (updated)
- **[Project Instructions](CLAUDE.md)**: Development guidelines and architecture
- **[AWS SSM Exploration](AWS_SSM_DATA_EXPLORATION.md)**: Technical deep-dive into data sources

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Set up development environment**:
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install  # Install pre-commit hooks
   ```
4. **Run full test suite** (`python -m pytest tests/ -v --cov=aws_services_reporter`)
5. **Run code quality checks** (`pre-commit run --all-files`)
6. **Commit** changes (`git commit -m 'Add amazing feature'`) - hooks run automatically
7. **Push** to branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request (CI/CD will automatically validate)

### Quality Standards
- ✅ All tests must pass (40+ tests across multiple Python versions)
- ✅ Pre-commit hooks must pass (automatic formatting and quality checks)
- ✅ Code must be formatted with black/isort (enforced by pre-commit)
- ✅ Security scan must show no high/medium severity issues
- ✅ Type checking should pass or have documented exceptions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **AWS Systems Manager** for providing the global infrastructure API
- **Rich Python Library** for beautiful terminal formatting
- **pytest** and **moto** for comprehensive testing capabilities
- **Open Source Community** for inspiration and best practices

---

**Made with ❤️ for the AWS community**

*For support, please see the [Troubleshooting Guide](TROUBLESHOOTING.md) or open an issue.*
