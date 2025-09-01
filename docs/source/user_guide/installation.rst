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

AWS Credentials Setup
---------------------

The tool requires AWS credentials with SSM read permissions. Choose one method:

**Option 1: AWS CLI Configuration**::

    aws configure

**Option 2: Environment Variables**::

    export AWS_ACCESS_KEY_ID=your-key-id
    export AWS_SECRET_ACCESS_KEY=your-secret-key
    export AWS_DEFAULT_REGION=us-east-1

**Option 3: IAM Role (EC2/Lambda)**

If running on AWS infrastructure, attach an IAM role with the following policy::

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:GetParameter",
                    "ssm:GetParameters"
                ],
                "Resource": "arn:aws:ssm:*:*:parameter/aws/service/global-infrastructure/*"
            }
        ]
    }

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
