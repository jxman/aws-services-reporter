"""AWS session management for the Services Reporter.

Handles AWS credential management, profile configuration, and session creation.
"""

import boto3

from ..core.config import Config


def create_session(config: Config) -> boto3.Session:
    """Create boto3 session with profile configuration.

    Args:
        config: Configuration object containing AWS profile information

    Returns:
        Configured boto3 Session instance
    """
    if config.aws_profile:
        return boto3.Session(profile_name=config.aws_profile)
    else:
        return boto3.Session()
