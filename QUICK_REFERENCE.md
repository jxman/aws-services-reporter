# AWS Services Reporter - Quick Reference

> **Version 1.4.1** | **CI/CD**: ✅ Passing | **Security**: ✅ Hardened | **Tests**: 52+ passing | **RSS**: 📡 Integrated

## 🚀 **Quick Start**

```bash
python main.py                    # Basic run (90 seconds first time, 5 seconds after)
python main.py --examples         # Show all examples
python main.py --help             # Show all options
```

## 🔄 **Cache Commands** (99% Time Savings!)

```bash
python main.py --cache-stats       # Show cache info
python main.py --cache-help        # Explain caching system
python main.py --no-cache          # Force fresh data
python main.py --clear-cache       # Delete cache
python main.py --cache-hours 1     # Cache for 1 hour only
```

## 📊 **Output Formats** (Organized in `reports/` subdirectories)

```bash
python main.py --format csv               # reports/csv/ (default)
python main.py --format json              # reports/json/ with metadata
python main.py --format excel             # reports/excel/ with multiple sheets
python main.py --format region-summary    # reports/csv/ region summary only
python main.py --format csv json excel    # All formats in subdirectories
python main.py --format csv region-summary# CSV + region summary
# Cache automatically saved to reports/cache/
```

## ⚙️ **Performance**

```bash
python main.py --max-workers 15     # Faster (more concurrent calls)
python main.py --max-retries 5      # More resilient
python main.py --quiet              # Silent mode
```

## ☁️ **AWS Config**

```bash
python main.py --profile prod       # Use AWS profile
python main.py --region us-west-2   # Change region
```

## 📁 **Custom Output**

```bash
python main.py --output-dir ./reports
python main.py --regions-file my_regions.csv
python main.py --matrix-file my_matrix.csv
```

## 🛠️ **Development & Testing**

```bash
# Run tests (same as CI/CD pipeline)
python -m pytest tests/ -v --cov=aws_services_reporter --cov-report=term-missing

# Code quality checks (same as CI/CD)
black --check . && isort --check-only . && flake8 .

# Security scan (same as CI/CD) - should show no issues
bandit -r . --severity-level medium

# Type checking (same as CI/CD)
mypy aws_services_reporter/ main.py --ignore-missing-imports

# Format code (development)
black . && isort .
```

## 🔧 **Common Combinations**

```bash
# Development (fast cache, JSON output)
python main.py --cache-hours 1 --format json

# Production (all formats, custom dir)
python main.py --format csv json excel --output-dir ./prod_reports

# Performance optimized
python main.py --max-workers 15 --quiet --format json

# Fresh data with all formats
python main.py --no-cache --format csv json excel
```

## 🆘 **Troubleshooting**

```bash
python main.py --log-level DEBUG    # Detailed logs
python main.py --cache-stats        # Check cache status  
python main.py --version            # Show version

# Development troubleshooting
python -m pytest tests/test_cache.py -v      # Test cache system
python -m pytest tests/ -k "output" -v      # Test output formats
python -m pytest tests/ --lf                # Re-run last failed tests

# Check CI/CD status
gh run list --limit 5                       # Recent workflow runs
gh run view --web                            # Open latest run in browser
```

## 🔐 **Security & Requirements** (v1.4.1)

### Security Dependencies
- `defusedxml>=0.7.1` - Secure XML parsing (RSS feeds)
- `requests>=2.28.0` - Secure HTTP handling
- `bandit` - Security scanning (dev dependency)

### Security Features
- ✅ **Zero high/medium security issues** (bandit validated)
- 🛡️ **URL scheme validation** (HTTPS/HTTP only)
- 🔒 **Secure XML parsing** prevents XXE attacks
- 📡 **Safe RSS processing** with input validation

## 📋 **All Available Options**

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--examples` | Show usage examples |
| `--cache-help` | Explain caching system |
| `--version` | Show version |
| `--output-dir DIR` | Output directory |
| `--regions-file FILE` | Regions CSV filename |
| `--matrix-file FILE` | Matrix CSV filename |
| `--max-workers N` | Concurrent threads (default: 10) |
| `--max-retries N` | Retry attempts (default: 3) |
| `--no-cache` | Disable caching |
| `--cache-hours N` | Cache TTL hours (default: 24) |
| `--cache-file FILE` | Cache file location (default: cache/aws_data_cache.json) |
| `--clear-cache` | Clear cache and exit |
| `--cache-stats` | Show cache stats and exit |
| `--format FORMAT [FORMAT ...]` | Output formats: csv, json, excel, region-summary |
| `--profile PROFILE` | AWS profile |
| `--region REGION` | AWS region (default: us-east-1) |
| `--log-level LEVEL` | DEBUG, INFO, WARNING, ERROR |
| `--quiet` | Suppress output |

## 🔒 **Security & CI/CD**

```bash
# View security reports (download from GitHub Actions)
gh run download --name security-reports

# Trigger CI/CD pipeline (by pushing commits)
git add . && git commit -m "feat: your changes" && git push

# View CI/CD results
gh run list --limit 3              # Recent runs
gh run view [RUN_ID]               # Detailed run info
```

## 📊 **Current Project Status**

| Component | Status | Notes |
|-----------|--------|---------|
| **Core Functionality** | ✅ Complete | All features working |
| **Modular Architecture** | ✅ Complete | Clean, maintainable code |
| **CI/CD Pipeline** | ✅ Operational | All tests passing |
| **Security Scanning** | ✅ Excellent | Zero high/medium issues |
| **Test Coverage** | ✅ 80%+ | 40 tests across Python 3.8-3.11 |
| **Documentation** | ✅ Complete | Comprehensive guides |
| **Production Ready** | ✅ Yes | Fully validated and tested |
| **Project Cleanup** | ✅ Complete | Obsolete files removed |

---

**Tips**:

- Use `python main.py --examples` for detailed usage examples
- Check `README.md` for complete documentation with security details
- View `ROADMAP.md` for completed milestones and future plans
