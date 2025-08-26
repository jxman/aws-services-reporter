# AWS Services Reporter - Quick Reference

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
python main.py --format csv              # reports/csv/ (default)
python main.py --format json             # reports/json/ with metadata
python main.py --format excel            # reports/excel/ with sheets  
python main.py --format csv json excel   # All formats in subdirectories
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
```

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
| `--format FORMAT [FORMAT ...]` | Output formats: csv, json, excel |
| `--profile PROFILE` | AWS profile |
| `--region REGION` | AWS region (default: us-east-1) |
| `--log-level LEVEL` | DEBUG, INFO, WARNING, ERROR |
| `--quiet` | Suppress output |

---
**Tip**: Use `python main.py --examples` for detailed usage examples with explanations!