"""
Configuration Management

This module handles loading configuration from environment variables.
"""

import os
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for the Berlin Service Appointment Monitor."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        
        # GitHub configuration
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPOSITORY', self._get_repo_from_context())
        
        # Email notification configuration
        self.notification_email = os.getenv('NOTIFICATION_EMAIL')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        # Webhook configuration
        self.webhook_url = os.getenv('WEBHOOK_URL')
        
        # Scraping configuration
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 minutes default
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        
        # Logging configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        self._validate_config()
        self._log_config()
    
    def _get_repo_from_context(self) -> str:
        """
        Try to get repository name from GitHub Actions context.
        
        Returns:
            Repository name in format 'owner/repo' or empty string
        """
        return os.getenv('GITHUB_REPOSITORY', '')
    
    def _validate_config(self):
        """Validate that required configuration is present."""
        
        # At least one notification method should be configured
        has_notification = any([
            self.github_token and self.github_repo,
            self.notification_email and self.email_password,
            self.webhook_url
        ])
        
        if not has_notification:
            logger.warning(
                "No notification methods configured. "
                "Please set up at least one of: GitHub token, email, or webhook."
            )
    
    def _log_config(self):
        """Log the current configuration (without sensitive data)."""
        
        logger.info("Configuration loaded:")
        logger.info(f"  GitHub repo: {self.github_repo or 'Not configured'}")
        logger.info(f"  GitHub token: {'Configured' if self.github_token else 'Not configured'}")
        logger.info(f"  Email: {'Configured' if self.notification_email else 'Not configured'}")
        logger.info(f"  Webhook: {'Configured' if self.webhook_url else 'Not configured'}")
        logger.info(f"  Check interval: {self.check_interval} seconds")
        logger.info(f"  Request timeout: {self.request_timeout} seconds")
        logger.info(f"  Log level: {self.log_level}")
    
    @property
    def has_github_config(self) -> bool:
        """Check if GitHub notification is properly configured."""
        return bool(self.github_token and self.github_repo)
    
    @property
    def has_email_config(self) -> bool:
        """Check if email notification is properly configured."""
        return bool(self.notification_email and self.email_password)
    
    @property
    def has_webhook_config(self) -> bool:
        """Check if webhook notification is properly configured."""
        return bool(self.webhook_url)