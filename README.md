# AWS Services Reporter

> **Comprehensive AWS service availability analysis tool with intelligent caching and multiple output formats**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.3.0-orange.svg)](CHANGELOG.md)

## 📋 Overview

AWS Services Reporter is a powerful Python tool that analyzes AWS service availability across all regions, providing comprehensive reports in multiple formats. With intelligent caching and concurrent processing, it transforms a 90-second AWS API crawl into a 5-second cached operation - delivering **99% performance improvement**.

### ✨ Key Features

- 🚀 **Intelligent Caching**: 99% performance improvement (90s → 5s)
- 🌍 **Complete Coverage**: All AWS regions and 400+ services  
- 📊 **Multiple Formats**: CSV, JSON, Excel with rich metadata
- ⚡ **Concurrent Processing**: 10 concurrent API calls by default
- 🎯 **Rich Progress Tracking**: Beautiful progress bars and status displays
- 🏗️ **Modular Architecture**: Clean, maintainable, and extensible code
- 🔧 **Comprehensive CLI**: 20+ command-line options
- 📈 **Detailed Statistics**: Service coverage, regional analysis, and metadata

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
│   │   └── ssm_client.py         # SSM Parameter Store client
│   ├── output/                   # Report generation
│   │   ├── csv_output.py         # CSV report generation
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
├── .github/workflows/            # CI/CD pipeline
├── main.py                       # Application entry point
├── requirements.txt              # Runtime dependencies
├── requirements-dev.txt          # Development dependencies
└── docs/                         # Documentation
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd aws-services

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
python main.py --format csv json excel
```

## 📊 Performance Comparison

| Run Type | Duration | API Calls | Data Source |
|----------|----------|-----------|-------------|
| **First Run** | ~90 seconds | 800+ calls | AWS API |
| **Cached Run** | ~5 seconds | 0 calls | Local cache |
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

## 📋 Output Formats

### 1. CSV Reports (`reports/csv/`)
- **regions_services.csv**: Each region with its available services
- **services_regions_matrix.csv**: Service × Region availability matrix

### 2. JSON Report (`reports/json/`)
- **regions_services.json**: Complete data with statistics and metadata
- Includes service coverage percentages and regional analysis

### 3. Excel Report (`reports/excel/`) - requires pandas + openpyxl
- **regions_services.xlsx**: Multi-sheet workbook with formatted data
- Includes statistics, conditional formatting, and charts

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

## 🛠️ Development

### Requirements
- **Python 3.8+**
- **boto3** (AWS SDK)
- **rich** (Enhanced UI)
- **tabulate** (Table formatting)
- **Optional**: pandas + openpyxl (Excel output)

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/ -v --cov

# Run type checking
mypy main.py --ignore-missing-imports

# Format code
black .
isort .
flake8 .
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_cache.py -v
python -m pytest tests/test_aws_integration.py -v

# Run with coverage
python -m pytest tests/ --cov=aws_services_reporter --cov-report=html
```

## 📚 Documentation

- **[Quick Reference](QUICK_REFERENCE.md)**: Command cheat sheet and common patterns
- **[Troubleshooting Guide](TROUBLESHOOTING.md)**: Common issues and solutions
- **[Development Roadmap](ROADMAP.md)**: Planned features and improvements
- **[Change Log](CHANGELOG.md)**: Version history and updates

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Run tests** (`python -m pytest tests/`)
4. **Commit** changes (`git commit -m 'Add amazing feature'`)
5. **Push** to branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

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