# AWS IAM Least Privilege Analysis - AWS Services Reporter

This document provides a comprehensive analysis of the IAM permissions required by the AWS Services Reporter, confirming that the current policy follows least privilege security principles.

## Overview

The AWS Services Reporter is a read-only tool that analyzes AWS service availability across regions by querying AWS Systems Manager (SSM) Parameter Store. This analysis validates that the required IAM permissions are minimal, appropriate, and secure.

## Current IAM Policy

The tool requires the following IAM policy:

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

## ✅ Least Privilege Analysis

### Required Actions Analysis

| Action | Purpose | Justification | Risk Level |
|--------|---------|---------------|------------|
| `ssm:GetParametersByPath` | Lists parameters under a path | Required to discover regions and services | ✅ **Low** - Read-only |
| `ssm:GetParameter` | Retrieves individual parameter values | Required to get region names, service details | ✅ **Low** - Read-only |

### Resource Scope Analysis

**✅ Appropriately Restricted:**
- **Path**: `/aws/service/global-infrastructure/*`
- **Type**: AWS-managed public infrastructure parameters only
- **Access**: Read-only to publicly available data
- **Exclusions**: No access to customer-created parameters or sensitive data

### Specific Parameters Accessed

#### Region Information
- `/aws/service/global-infrastructure/regions` - List of all AWS regions
- `/aws/service/global-infrastructure/regions/{region_code}/longName` - Region display names
- `/aws/service/global-infrastructure/regions/{region_code}/launchDate` - Region launch dates
- `/aws/service/global-infrastructure/regions/{region_code}/partition` - Region partition (aws, aws-gov, aws-cn)
- `/aws/service/global-infrastructure/regions/{region_code}/availability-zones` - AZ count per region

#### Service Information
- `/aws/service/global-infrastructure/services` - List of all AWS services
- `/aws/service/global-infrastructure/services/{service_code}/regions` - Regions where service is available
- `/aws/service/global-infrastructure/services/{service_code}/longName` - Service display names

## Security Validation

### ✅ What This Policy ALLOWS (Appropriate)
- **Read-only access** to AWS public infrastructure parameters
- **Service discovery** across all AWS regions
- **Region metadata** including names, launch dates, and availability zones
- **Service availability mapping** per region
- **Public information only** - no customer data or configurations

### ✅ What This Policy PREVENTS (Good Security)
- ❌ **Cannot access** user-created SSM parameters
- ❌ **Cannot access** other AWS service APIs (EC2, S3, Lambda, etc.)
- ❌ **Cannot write, update, or delete** any resources
- ❌ **Cannot access** customer-specific infrastructure data
- ❌ **Cannot access** parameters outside `/aws/service/global-infrastructure/`
- ❌ **Cannot access** sensitive configuration or credential parameters

### Additional Security Features

#### RSS Client Security (v1.4.0+)
- **HTTPS only** connections to AWS documentation RSS feed
- **No additional AWS permissions** required
- **Graceful fallback** if RSS feed is unavailable
- **Input validation** for all external URLs

#### Application Security
- **Defensive programming** with comprehensive error handling
- **Rate limiting** with exponential backoff to prevent API abuse
- **Secure XML parsing** using `defusedxml` library
- **No credential storage** - uses standard AWS SDK credential chain

## Risk Assessment

### Overall Risk Level: ✅ **MINIMAL**

| Risk Category | Assessment | Justification |
|---------------|------------|---------------|
| **Data Exposure** | ✅ **None** | Only accesses publicly available AWS infrastructure data |
| **Privilege Escalation** | ✅ **None** | Read-only permissions with no write/admin capabilities |
| **Lateral Movement** | ✅ **None** | Limited to specific SSM parameter paths only |
| **Resource Impact** | ✅ **None** | Cannot create, modify, or delete any AWS resources |
| **Cost Impact** | ✅ **Minimal** | Only SSM GetParameter API calls (typically <$1/month) |

## Alternative Policy Options

### Option 1: Current Policy (Recommended)
**Pros:**
- ✅ Simple and maintainable
- ✅ Properly scoped to AWS public infrastructure
- ✅ Future-proof for new regions/services
- ✅ Clear security boundary

**Cons:**
- None identified

### Option 2: Ultra-Restrictive Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["ssm:GetParametersByPath"],
            "Resource": [
                "arn:aws:ssm:*:*:parameter/aws/service/global-infrastructure/regions",
                "arn:aws:ssm:*:*:parameter/aws/service/global-infrastructure/services"
            ]
        },
        {
            "Effect": "Allow",
            "Action": ["ssm:GetParameter"],
            "Resource": [
                "arn:aws:ssm:*:*:parameter/aws/service/global-infrastructure/regions/*",
                "arn:aws:ssm:*:*:parameter/aws/service/global-infrastructure/services/*"
            ]
        }
    ]
}
```

**Pros:**
- ✅ More granular resource specification

**Cons:**
- ❌ More complex to maintain
- ❌ No additional security benefit
- ❌ May break with future AWS parameter structure changes

## Compliance Considerations

### Industry Standards Alignment

#### SOC 2 Type II
- ✅ **Principle of Least Privilege** - Minimal permissions granted
- ✅ **Data Classification** - Only public data accessed
- ✅ **Access Control** - Appropriate restrictions in place

#### ISO 27001
- ✅ **Access Rights Management** - Limited to required parameters only
- ✅ **Information Security Risk Management** - Low risk profile
- ✅ **Secure System Engineering** - Read-only architecture

#### NIST Cybersecurity Framework
- ✅ **Identify** - Clear inventory of required permissions
- ✅ **Protect** - Appropriate access controls implemented
- ✅ **Detect** - CloudTrail logging for all API calls

## Monitoring and Auditing

### Recommended CloudTrail Events
Monitor these events for security auditing:
- `GetParametersByPath` calls to `/aws/service/global-infrastructure/*`
- `GetParameter` calls to specific infrastructure parameters
- Any `AccessDenied` errors indicating potential misuse

### Normal Usage Patterns
- **Frequency**: Typically daily or on-demand runs
- **Volume**: 800-1000 API calls per execution
- **Duration**: 60-90 seconds for fresh data collection
- **Regions**: Queries all available AWS regions

## Conclusion

### ✅ **APPROVED - Current IAM Policy is Optimal**

The current IAM policy for the AWS Services Reporter follows least privilege principles and is **recommended for production use** because:

1. **✅ Minimal Permissions** - Only 2 read-only SSM actions required
2. **✅ Appropriate Scope** - Limited to AWS public infrastructure parameters
3. **✅ No Write Access** - Cannot modify any resources
4. **✅ No Sensitive Data** - Accesses only publicly available information
5. **✅ Clear Security Boundary** - Well-defined parameter path restrictions
6. **✅ Maintainable** - Simple policy structure that scales with AWS growth

### Security Recommendations

1. **✅ Use the current policy as-is** - it provides optimal security with minimal complexity
2. **✅ Enable CloudTrail logging** for audit trails of SSM API usage
3. **✅ Regular access reviews** - Verify users with this policy still require access
4. **✅ Consider AWS Organizations SCPs** for additional guardrails in multi-account environments

---

**Document Version**: 1.0  
**Last Updated**: September 1, 2025  
**Reviewed By**: Claude Code Analysis  
**Next Review**: Annual or upon policy changes
