# AWS Services Reporter - Troubleshooting Guide

## Common Issues and Solutions

### Installation and Setup Issues

#### Python Version Compatibility
**Problem**: Import errors or syntax issues
```bash
AttributeError: module 'collections' has no attribute 'Iterable'
```
**Solution**: Use Python 3.8+ (recommended 3.10+)
```bash
python --version  # Should show 3.8+
pip install --upgrade pip setuptools
```

#### Dependency Installation Failures
**Problem**: Package installation fails
```bash
error: externally-managed-environment
```
**Solution**: Use virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### Missing Optional Dependencies
**Problem**: Excel output doesn't work

```text
Excel output requires pandas and openpyxl
```

**Solution**: Install optional dependencies
```bash
pip install pandas openpyxl
# OR install all dependencies
pip install -r requirements.txt
```

### AWS Configuration Issues

#### AWS Credentials Not Found
**Problem**:

```text
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

**Solutions**:
1. **AWS CLI Configuration**:
   ```bash
   aws configure
   # Enter: Access Key, Secret Key, Region, Output Format
   ```

2. **Environment Variables**:
   ```bash
   export AWS_ACCESS_KEY_ID="your-access-key"
   export AWS_SECRET_ACCESS_KEY="your-secret-key"
   export AWS_DEFAULT_REGION="us-east-1"
   ```

3. **IAM Role** (EC2/Lambda):
   ```bash
   # Ensure role has SSM permissions
   # No additional configuration needed
   ```

4. **AWS Profile**:
   ```bash
   python main.py --profile your-profile-name
   ```

#### Permission Denied Errors
**Problem**:

```text
botocore.exceptions.ClientError: An error occurred (AccessDenied)
```

**Solution**: Ensure your AWS credentials have these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParametersByPath",
                "ssm:GetParameter"
            ],
            "Resource": [
                "arn:aws:ssm:*:*:parameter/aws/service/global-infrastructure/*"
            ]
        }
    ]
}
```

#### Region Access Issues
**Problem**: Some regions not accessible

```text
botocore.exceptions.ClientError: An error occurred (UnauthorizedOperation)
```

**Solutions**:
1. **Check region availability**:
   ```bash
   aws ec2 describe-regions --region us-east-1
   ```

2. **Use different base region**:
   ```bash
   python main.py --region us-west-2
   ```

3. **Service Control Policies (SCPs)**: Contact your AWS administrator

### Performance and Timeout Issues

#### Slow Execution
**Problem**: Script runs for several minutes
**Solutions**:
1. **Enable caching** (default):
   ```bash
   python main.py  # Uses 24-hour cache
   ```

2. **Check cache status**:
   ```bash
   python main.py --cache-stats
   ```

3. **Adjust worker count**:
   ```bash
   python main.py --max-workers 20  # Increase concurrency
   ```

4. **Use longer cache**:
   ```bash
   python main.py --cache-hours 72  # 3-day cache
   ```

#### Connection Timeouts
**Problem**:

```text
botocore.exceptions.ConnectTimeoutError: Connect timeout
```

**Solutions**:
1. **Increase retries**:
   ```bash
   python main.py --max-retries 5
   ```

2. **Check network connectivity**:
   ```bash
   aws sts get-caller-identity  # Test AWS connectivity
   ```

3. **Use VPN/proxy settings** if behind corporate firewall

#### Rate Limiting
**Problem**:

```text
botocore.exceptions.ClientError: Throttling
```

**Solution**: Built-in exponential backoff handles this automatically. If persistent:
```bash
python main.py --max-workers 5  # Reduce concurrency
```

### Output and File Issues

#### Output File Locations (v1.3.0+)
**Organized Directory Structure**: All outputs are organized in subdirectories under `reports/`:

```text
reports/
├── csv/                    # CSV reports
│   ├── regions_services.csv
│   └── services_regions_matrix.csv
├── json/                   # JSON reports  
│   └── regions_services.json
├── excel/                  # Excel reports
│   └── regions_services.xlsx
└── cache/                  # Cache files
    └── aws_data_cache.json
```

**Note**: Legacy files in the root `reports/` directory are automatically cleaned up.

#### Permission Denied on File Write
**Problem**:

```text
PermissionError: [Errno 13] Permission denied: './output.csv'
```

**Solutions**:
1. **Change output directory**:
   ```bash
   python main.py --output-dir ~/aws-reports/
   ```

2. **Check file permissions**:
   ```bash
   ls -la ./output.csv
   chmod 644 ./output.csv
   ```

#### Corrupted Cache File
**Problem**: Cache errors or invalid data
**Solution**: Clear and rebuild cache:

```bash
python main.py --clear-cache
python main.py  # Rebuilds cache
```

#### Excel Output Issues
**Problem**: Excel files not generated
**Solutions**:
1. **Install dependencies**:
   ```bash
   pip install pandas openpyxl
   ```

2. **Check for write permissions** in output directory

3. **Use alternative formats**:
   ```bash
   python main.py --format json csv  # Skip Excel
   ```

### Data and Format Issues

#### Empty or Missing Data
**Problem**: Output files contain no data
**Solutions**:
1. **Check AWS permissions** (see permission section above)

2. **Verify region accessibility**:
   ```bash
   python main.py --region us-east-1 --quiet
   ```

3. **Clear corrupted cache**:
   ```bash
   python main.py --clear-cache
   ```

#### Character Encoding Issues
**Problem**: Special characters not displayed correctly
**Solutions**:
1. **Use UTF-8 compatible tools** (Excel 2016+, LibreOffice)

2. **Check JSON output**:
   ```bash
   python main.py --format json
   cat regions_services.json  # Should display correctly
   ```

## Advanced Troubleshooting

### Debug Mode
Enable detailed logging for troubleshooting:
```bash
python main.py --log-level DEBUG --quiet=false
```

### Network Diagnostics
Test AWS connectivity:
```bash
# Test basic AWS access
aws sts get-caller-identity

# Test SSM access
aws ssm get-parameters-by-path --path "/aws/service/global-infrastructure/regions" --region us-east-1

# Test specific region
aws ssm get-parameter --name "/aws/service/global-infrastructure/regions/us-east-1/longName" --region us-east-1
```

### Cache Diagnostics

```bash
# View cache statistics
python main.py --cache-stats

# Clear and rebuild cache
python main.py --clear-cache
python main.py --cache-hours 1  # Short cache for testing

# Test without cache
python main.py --no-cache --max-workers 5
```

### Performance Profiling

```bash
# Time execution
time python main.py --quiet

# Profile with minimal output
python main.py --format csv --quiet --max-workers 1

# Test different regions
python main.py --region eu-west-1 --quiet
```

## Getting Help

### Log Analysis
Most issues can be diagnosed from logs:

```bash
python main.py --log-level DEBUG 2>&1 | tee debug.log
```

Common log patterns:
- `ClientError: AccessDenied` → Permissions issue
- `ConnectTimeoutError` → Network issue  
- `Throttling` → Rate limiting (normal, will retry)
- `ImportError` → Missing dependencies

### Environment Information
When reporting issues, include:

```bash
python --version
pip list | grep -E "(boto3|rich|pandas)"
aws --version
echo $AWS_DEFAULT_REGION
python main.py --version
```

### Support Resources
- **GitHub Issues**: Report bugs and feature requests
- **AWS Documentation**: [Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- **AWS CLI Documentation**: [Configuration Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)

## Performance Optimization

### Best Practices
1. **Use caching** for repeated runs (default 24 hours)
2. **Adjust worker count** based on network capacity (default: 10)
3. **Choose appropriate output formats** (CSV is fastest)
4. **Use specific regions** when possible
5. **Monitor cache effectiveness** with `--cache-stats`

### Benchmark Results
- **Without cache**: ~90 seconds (varies by region count)
- **With cache**: ~5 seconds (99% improvement)
- **Optimal workers**: 10-20 (depends on network/AWS limits)
- **Memory usage**: <50MB for typical datasets

### Production Usage
For automated/production use:

```bash
# Robust production command
python main.py \
  --format json csv \
  --cache-hours 24 \
  --max-workers 10 \
  --max-retries 3 \
  --log-level INFO \
  --quiet \
  --output-dir /var/reports/aws/
```
