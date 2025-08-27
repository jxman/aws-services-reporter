# AWS SSM Parameter Store - Public Data Exploration

This document provides a comprehensive overview of the publicly available data in AWS Systems Manager Parameter Store that could be leveraged to enhance the AWS Services Reporter with richer insights and additional reporting capabilities.

## Current Implementation Status

The AWS Services Reporter currently uses:
- **Basic service codes** (e.g., `ec2`, `s3`, `lambda`)
- **Regional service availability** (which regions each service is available in)
- **Region codes and names** (e.g., `us-east-1` → `US East (N. Virginia)`)

## Available Data Categories

### 1. AWS Global Infrastructure Data

#### Region Information
- **Path**: `/aws/service/global-infrastructure/regions`
- **Content**: List of all AWS region codes
- **Example**: `us-east-1`, `eu-west-1`, `ap-southeast-1`

- **Path**: `/aws/service/global-infrastructure/regions/{region}/longName`
- **Content**: Full region names
- **Example**: `US East (N. Virginia)`, `Europe (Ireland)`

#### Availability Zone Information
- **Path**: `/aws/service/global-infrastructure/availability-zones`
- **Content**: All availability zones across regions
- **Example**: `us-east-1a`, `us-east-1b`, `us-east-1c`

- **Path**: `/aws/service/global-infrastructure/regions/{region}/availability-zones`
- **Content**: AZs for specific regions

#### AWS Local Zones
- **Path**: `/aws/service/global-infrastructure/local-zones`
- **Content**: AWS Local Zone locations
- **Use Case**: Mobile edge computing and ultra-low latency applications

#### AWS Wavelength Zones
- **Path**: `/aws/service/global-infrastructure/wavelength-zones`
- **Content**: Wavelength zone information
- **Use Case**: 5G edge computing locations

### 2. Enhanced Service Information

#### Service Display Names
- **Path**: `/aws/service/global-infrastructure/services/{service_code}/longName`
- **Content**: Human-readable service names
- **Examples**:
  - `ec2` → `Amazon Elastic Compute Cloud`
  - `s3` → `Amazon Simple Storage Service`
  - `lambda` → `AWS Lambda`
  - `rds` → `Amazon Relational Database Service`
  - `bedrock` → `Amazon Bedrock`

#### Service Descriptions
- **Path**: `/aws/service/global-infrastructure/services/{service_code}/description`
- **Content**: Service descriptions and use cases
- **Example**: `ec2` → `Secure and resizable compute capacity in the cloud`

#### Service Categories
- **Path**: `/aws/service/global-infrastructure/services/{service_code}/category`
- **Content**: Service categorization
- **Categories**: `Compute`, `Storage`, `Database`, `Networking`, `Machine Learning`, `Analytics`, `Security`, `Developer Tools`

#### Service Launch Information
- **Path**: `/aws/service/global-infrastructure/services/{service_code}/launchDate`
- **Content**: When the service was first launched globally
- **Format**: ISO date format (e.g., `2006-08-24`)

#### Regional Service Launch Dates
- **Path**: `/aws/service/global-infrastructure/regions/{region}/services/{service_code}/launchDate`
- **Content**: When service became available in specific regions
- **Use Case**: Track regional rollout timeline and expansion patterns

#### Service Status Information
- **Path**: `/aws/service/global-infrastructure/services/{service_code}/status`
- **Content**: Global service availability status
- **Values**: `available`, `preview`, `discontinued`

#### Regional Service Status
- **Path**: `/aws/service/global-infrastructure/regions/{region}/services/{service_code}/status`
- **Content**: Regional service status
- **Values**: `available`, `preview`, `pending`, `deprecated`, `limited`

### 3. Region Status and Lifecycle Data

#### Region Launch Dates
- **Path**: `/aws/service/global-infrastructure/regions/{region}/launchDate`
- **Content**: When the AWS region was first launched
- **Examples**:
  - `us-east-1`: `2006-08-24` (first region)
  - `eu-west-1`: `2008-12-10`
  - `me-central-1`: `2022-08-30` (recent region)
  - `ap-southeast-5`: `2024-05-02` (Malaysia - very recent)

#### Region Status
- **Path**: `/aws/service/global-infrastructure/regions/{region}/status`
- **Content**: Current operational status
- **Values**:
  - `available` - Fully operational
  - `preview` - Limited preview access
  - `pending` - Announced but not yet launched
  - `deprecated` - Being phased out (rare)

#### Region Announcements
- **Path**: `/aws/service/global-infrastructure/regions/{region}/announcementDate`
- **Content**: When the region was first announced (before launch)
- **Use Case**: Track announcement-to-launch timelines

#### Region Opt-In Requirements
- **Path**: `/aws/service/global-infrastructure/regions/{region}/optInRequired`
- **Content**: Whether the region requires explicit opt-in
- **Values**: `true`/`false`
- **Examples**: Newer regions like `ap-east-1` (Hong Kong), `me-central-1` (UAE) require opt-in

#### Regional Categories
- **Path**: `/aws/service/global-infrastructure/regions/{region}/category`
- **Values**:
  - `standard` - Standard commercial regions
  - `govcloud` - Government cloud regions
  - `china` - China regions (special partnership)
  - `wavelength` - Wavelength zones
  - `local` - Local zones

### 4. AMI and Instance Information

#### Amazon Linux AMIs
- **Path**: `/aws/service/ami-amazon-linux-latest/`
- **Content**: Latest Amazon Linux AMI IDs
- **Example**: `/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2`

#### Windows AMIs
- **Path**: `/aws/service/ami-windows-latest/`
- **Content**: Latest Windows Server AMI IDs
- **Example**: `/aws/service/ami-windows-latest/Windows_Server-2022-English-Full-Base`

#### ECS Optimized AMIs
- **Path**: `/aws/service/ecs/optimized-ami/`
- **Content**: ECS-optimized AMI IDs
- **Example**: `/aws/service/ecs/optimized-ami/amazon-linux-2/recommended`

#### EC2 Instance Types
- **Path**: `/aws/service/ec2/instance-type/`
- **Content**: Available EC2 instance types and specifications
- **Use Case**: Instance family availability per region

### 5. Service Endpoints
- **Path**: `/aws/service/global-infrastructure/services/{service}/regions/{region}/endpoints`
- **Content**: Service endpoint URLs
- **Example**: S3 endpoints, EC2 endpoints per region
- **Use Case**: API endpoint discovery and regional connectivity

## Sample Enhanced Data Structures

### Enhanced Service Data
```json
{
  "ec2": {
    "code": "ec2",
    "longName": "Amazon Elastic Compute Cloud",
    "category": "Compute",
    "description": "Secure and resizable compute capacity in the cloud",
    "globalLaunchDate": "2006-08-24",
    "status": "available",
    "regionalInfo": {
      "us-east-1": {
        "status": "available",
        "launchDate": "2006-08-24"
      },
      "eu-west-1": {
        "status": "available", 
        "launchDate": "2008-12-10"
      },
      "ap-southeast-1": {
        "status": "available",
        "launchDate": "2010-04-28"
      }
    }
  },
  "bedrock": {
    "code": "bedrock",
    "longName": "Amazon Bedrock", 
    "category": "Machine Learning",
    "description": "Build and scale generative AI applications",
    "globalLaunchDate": "2023-09-28",
    "status": "available",
    "regionalInfo": {
      "us-east-1": {
        "status": "available",
        "launchDate": "2023-09-28"
      },
      "eu-west-1": {
        "status": "available",
        "launchDate": "2023-10-05"  
      },
      "ap-southeast-1": {
        "status": "pending",
        "expectedLaunchDate": "2024-Q2"
      }
    }
  }
}
```

### Enhanced Region Data
```json
{
  "regions": {
    "us-east-1": {
      "code": "us-east-1",
      "longName": "US East (N. Virginia)",
      "status": "available",
      "launchDate": "2006-08-24",
      "announcementDate": "2006-03-14",
      "optInRequired": false,
      "category": "standard",
      "serviceCount": 386,
      "availabilityZones": ["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1f"],
      "physicalLocation": {
        "country": "United States",
        "state": "Virginia"
      }
    },
    "me-central-1": {
      "code": "me-central-1", 
      "longName": "Middle East (UAE)",
      "status": "available",
      "launchDate": "2022-08-30",
      "announcementDate": "2021-10-28", 
      "optInRequired": true,
      "category": "standard",
      "serviceCount": 178,
      "availabilityZones": ["me-central-1a", "me-central-1b", "me-central-1c"]
    },
    "ap-southeast-5": {
      "code": "ap-southeast-5",
      "longName": "Asia Pacific (Malaysia)", 
      "status": "available",
      "launchDate": "2024-05-02",
      "announcementDate": "2023-11-27",
      "optInRequired": true,
      "category": "standard",
      "serviceCount": 146,
      "availabilityZones": ["ap-southeast-5a", "ap-southeast-5b", "ap-southeast-5c"]
    }
  }
}
```

### Regional Service Timeline
```json
{
  "regionalServiceTimeline": {
    "bedrock": {
      "us-east-1": {
        "status": "available",
        "launchDate": "2023-09-28",
        "announcementDate": "2023-04-13"
      },
      "eu-west-1": {
        "status": "available", 
        "launchDate": "2023-10-05"
      },
      "ap-southeast-1": {
        "status": "pending",
        "expectedLaunchDate": "2024-Q2",
        "announcementDate": "2024-01-15"
      }
    },
    "ec2": {
      "us-east-1": {
        "status": "available",
        "launchDate": "2006-08-24"
      },
      "eu-west-1": {
        "status": "available",
        "launchDate": "2008-12-10"
      }
    }
  }
}
```

## Potential New Report Types

### 1. Enhanced Service Catalog Report
```
Service Code | Full Name                    | Category         | Global Launch | Status    | Regions
ec2          | Amazon Elastic Compute Cloud | Compute          | 2006-08-24   | available | 37/37
bedrock      | Amazon Bedrock              | Machine Learning | 2023-09-28   | available | 15/37
s3           | Amazon Simple Storage Service| Storage          | 2006-03-14   | available | 37/37
```

### 2. Region Maturity Analysis
```
Region Code      | Launch Date | Age (Days) | Opt-In | Service Count | Service Coverage %
us-east-1       | 2006-08-24  | 6,710     | No     | 386          | 100%
eu-west-1       | 2008-12-10  | 5,837     | No     | 342          | 88.6%
me-central-1    | 2022-08-30  | 728       | Yes    | 178          | 46.1%
ap-southeast-5  | 2024-05-02  | 269       | Yes    | 146          | 37.8%
```

### 3. Service Rollout Timeline
```
Service  | Global Launch | First Region | Latest Region | Rollout Days | Regional Coverage
ec2      | 2006-08-24   | us-east-1    | ap-southeast-5| 6,461       | 37/37 (100%)
s3       | 2006-03-14   | us-east-1    | ap-southeast-5| 6,624       | 37/37 (100%)
bedrock  | 2023-09-28   | us-east-1    | eu-west-1    | 7           | 15/37 (40.5%)
```

### 4. Regional Expansion Analysis
- Track AWS's geographic expansion strategy over time
- Identify patterns in new region announcements vs. launches
- Analyze time-to-market for new regions
- Compare service availability growth across regions

### 5. Service Availability Gaps Report
```
Service         | Missing From Regions                    | Coverage | Pending Regions
bedrock        | ap-southeast-1, ca-central-1, sa-east-1 | 15/37   | ap-southeast-1 (Q2 2024)
sagemaker      | cn-north-1, cn-northwest-1             | 35/37   | None announced
comprehend     | af-south-1, ap-east-2, me-south-1      | 34/37   | TBD
```

### 6. Compliance and Governance Report
```
Region         | Opt-In Required | Category | Data Residency | Special Requirements
us-east-1     | No              | standard | US             | None
eu-west-1     | No              | standard | EU/GDPR        | GDPR compliance
me-central-1  | Yes             | standard | UAE            | Local data laws
us-gov-east-1 | Yes             | govcloud | US Government  | FedRAMP High
```

### 7. Historical Service Launch Analysis
- Track which services launched first in new regions
- Identify "pioneer services" vs "follower services"
- Analyze regional launch patterns (US-first vs global simultaneous)
- Compare announcement-to-availability timelines

### 8. Availability Zone Coverage
```
Region        | AZ Count | AZ Names                           | Local Zones | Wavelength
us-east-1     | 6        | 1a,1b,1c,1d,1e,1f                 | 12         | 8
eu-west-1     | 3        | 1a,1b,1c                          | 1          | 2
ap-southeast-5| 3        | 5a,5b,5c                          | 0          | 0
```

## Implementation Considerations

### Data Retrieval Strategy
1. **Incremental Enhancement**: Start with service display names and categories
2. **Caching Strategy**: Extended TTL for historical data (launch dates don't change)
3. **Performance Impact**: Additional API calls per service/region
4. **Rate Limiting**: More aggressive backoff for metadata requests

### New Configuration Options
```python
--include-metadata        # Include service descriptions and categories
--include-timeline       # Include launch dates and historical data
--include-status         # Include current status and pending services
--include-zones          # Include availability zone information
--format enhanced-csv    # New format with full metadata
--format timeline        # Chronological service rollout report
```

### Storage Considerations
- Enhanced cache structure to accommodate metadata
- Separate cache files for different data types
- Historical data preservation across cache refreshes

## Future Enhancement Ideas

### 1. Interactive Dashboard Data
- Service adoption timelines
- Regional expansion visualizations
- Service category distribution
- Launch velocity analysis

### 2. Predictive Analysis
- Predict which services will launch in which regions next
- Identify patterns in AWS expansion strategy
- Regional service gap analysis

### 3. Compliance and Planning Tools
- Data residency impact analysis
- Multi-region architecture planning
- Service availability forecasting

### 4. Integration Opportunities
- AWS Cost Explorer integration for service usage patterns
- CloudFormation template analysis for service dependencies
- AWS Config integration for compliance monitoring

## Technical Architecture Notes

### Current Limitations
- Only basic service codes retrieved
- No temporal data captured
- Limited regional metadata
- Single-format output approach

### Enhancement Approach
- Modular data fetching (on-demand metadata)
- Flexible caching system (different TTLs for different data types)
- Extensible output formats
- Configuration-driven feature enablement

---

**Document Version**: 1.0  
**Created**: August 27, 2024  
**Last Updated**: August 27, 2024  
**Related Project**: AWS Services Reporter v1.3.0

This document serves as a comprehensive reference for potential enhancements to the AWS Services Reporter, providing detailed information about available data sources and implementation possibilities for future development phases.