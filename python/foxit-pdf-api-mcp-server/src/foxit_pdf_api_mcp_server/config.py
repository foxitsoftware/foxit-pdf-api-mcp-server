"""Configuration management for Foxit PDF API MCP Server."""

import os
import sys
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Configuration for Foxit PDF API MCP Server."""

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        # API Base URL
        self.api_base_url = self._get_api_base_url()

        # API Credentials
        self.client_id = os.getenv("FOXIT_CLOUD_API_CLIENT_ID", "")
        self.client_secret = os.getenv("FOXIT_CLOUD_API_CLIENT_SECRET", "")

        # Validate credentials
        if not self.client_id or not self.client_secret:
            print(
                "Error: FOXIT_CLOUD_API_CLIENT_ID and FOXIT_CLOUD_API_CLIENT_SECRET "
                "environment variables are required",
                file=sys.stderr,
            )
            sys.exit(1)

        # Operation settings
        self.default_timeout = 300  # 5 minutes in seconds
        self.poll_interval = 2  # 2 seconds
        self.max_retries = 3

    def _get_api_base_url(self) -> str:
        """
        Get and validate API base URL from environment.

        Returns:
            Validated API base URL without trailing slashes

        Raises:
            SystemExit: If URL is invalid or not provided
        """
        default_url = "https://na1.fusion.foxit.com/pdf-services"

        # Try multiple environment variable names for compatibility
        url = (
            os.getenv("FOXIT_CLOUD_API_BASE_URL")
            or os.getenv("FOXIT_CLOUD_API_HOST")
            or default_url
        )

        if not url:
            print(
                "Error: FOXIT_CLOUD_API_BASE_URL or FOXIT_CLOUD_API_HOST "
                "environment variable is required",
                file=sys.stderr,
            )
            sys.exit(1)

        # Validate URL format
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
        except Exception as e:
            print(f"Error: Invalid API base URL format: {url}", file=sys.stderr)
            sys.exit(1)

        # Remove trailing slashes
        return url.rstrip("/")


# Global config instance
config = Config()
