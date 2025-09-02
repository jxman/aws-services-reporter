Installation Guide
==================

Requirements
------------

* Python 3.8 or higher
* AWS CLI configured or IAM role with SSM permissions
* Virtual environment (recommended)

Quick Installation
------------------

1. Clone the repository::

    git clone https://github.com/jxman/aws-services-reporter.git
    cd aws-services-reporter

2. Create and activate virtual environment::

    python3 -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # or
    .venv\Scripts\activate     # Windows

3. Install dependencies::

    pip install -r requirements.txt

AWS Credentials Setup (Required)
----------------------------------

**⚠️ IMPORTANT**: AWS credentials are required for this tool to function. The tool queries AWS Systems Manager Parameter Store and cannot operate without proper authentication.

**Required IAM Permissions (Least Privilege)**

All credential methods below must have the following IAM policy attached::

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:GetParametersByPath",
                    "ssm:GetParameter"
                ],
                "Resource": "arn:aws:ssm:*:*:parameter/aws/service/global-infrastructure/*"
            }
        ]
    }

**Credential Configuration Options**

Choose one of the following methods to provide AWS credentials:

**Option 1: AWS CLI Configuration (Recommended)**

Install and configure the AWS CLI with your credentials::

    # Install AWS CLI (if not already installed)
    pip install awscli

    # Configure credentials
    aws configure

This will prompt you for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (recommend: us-east-1)
- Output format (recommend: json)

**Option 2: Environment Variables**

Set AWS credentials as environment variables::

    export AWS_ACCESS_KEY_ID=your-key-id
    export AWS_SECRET_ACCESS_KEY=your-secret-key
    export AWS_DEFAULT_REGION=us-east-1

**Option 3: IAM Role (EC2/Lambda/ECS)**

If running on AWS infrastructure, attach an IAM role with the above policy.
No additional configuration needed - the tool will automatically use the instance role.

**Option 4: AWS SSO/Profile**

If using AWS SSO or named profiles::

    # Configure SSO or profile
    aws configure sso

    # Use specific profile with the tool
    python main.py --profile your-profile-name

**Credential Verification**

Test your AWS credentials setup::

    # Test AWS connectivity
    aws sts get-caller-identity

    # Test SSM parameter access
    aws ssm get-parameter --name "/aws/service/global-infrastructure/regions/us-east-1/longName" --region us-east-1

Development Installation
------------------------

For development and contributing::

    # Install development dependencies
    pip install -r requirements-dev.txt

    # Install pre-commit hooks
    pre-commit install

    # Run tests
    python -m pytest tests/ -v --cov

Verification
------------

Test your installation::

    python main.py --version
    python main.py --examples
