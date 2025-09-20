"""
Notification Manager

This module handles sending notifications through various channels:
- GitHub Issues
- Email
- Webhooks (Discord, Slack, etc.)
"""

import logging
import smtplib
import requests
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages sending notifications through multiple channels."""
    
    def __init__(self, config):
        self.config = config
        self.github_token = config.github_token
        self.github_repo = config.github_repo
        
    def send_notification(self, title: str, message: str) -> bool:
        """
        Send notification through all configured channels.
        
        Args:
            title: Notification title
            message: Notification message body
            
        Returns:
            True if at least one notification was sent successfully
        """
        success = False
        
        # Try GitHub Issues notification
        if self._send_github_issue(title, message):
            success = True
            
        # Try email notification
        if self._send_email(title, message):
            success = True
            
        # Try webhook notification
        if self._send_webhook(title, message):
            success = True
            
        return success
    
    def _send_github_issue(self, title: str, message: str) -> bool:
        """
        Create a GitHub issue with the notification.
        
        Args:
            title: Issue title
            message: Issue body
            
        Returns:
            True if issue was created successfully
        """
        try:
            if not self.github_token or not self.github_repo:
                logger.info("GitHub token or repo not configured, skipping GitHub issue")
                return False
                
            url = f"https://api.github.com/repos/{self.github_repo}/issues"
            
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            # Add timestamp and labels
            issue_body = f"{message}\n\n---\n*Created automatically at {datetime.now().isoformat()}*"
            
            data = {
                'title': title,
                'body': issue_body,
                'labels': ['appointment-alert', 'automated']
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            issue_url = response.json().get('html_url', 'Unknown')
            logger.info(f"GitHub issue created successfully: {issue_url}")
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.error(
                    "GitHub API permission denied. "
                    "This is normal when running locally. "
                    "Issues will be created automatically when running in GitHub Actions."
                )
            else:
                logger.error(f"GitHub API error ({e.response.status_code}): {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to create GitHub issue: {str(e)}")
            return False
    
    def _send_email(self, title: str, message: str) -> bool:
        """
        Send email notification.
        
        Args:
            title: Email subject
            message: Email body
            
        Returns:
            True if email was sent successfully
        """
        try:
            email = self.config.notification_email
            password = self.config.email_password
            
            if not email or not password:
                logger.info("Email credentials not configured, skipping email notification")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = email  # Send to self
            msg['Subject'] = title
            
            # Add body
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email using Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email, password)
            
            text = msg.as_string()
            server.sendmail(email, email, text)
            server.quit()
            
            logger.info(f"Email notification sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    def _send_webhook(self, title: str, message: str) -> bool:
        """
        Send webhook notification (Discord, Slack, etc.).
        
        Args:
            title: Notification title
            message: Notification message
            
        Returns:
            True if webhook was sent successfully
        """
        try:
            webhook_url = self.config.webhook_url
            
            if not webhook_url:
                logger.info("Webhook URL not configured, skipping webhook notification")
                return False
            
            # Format for Discord webhook (can be adapted for other services)
            if 'discord' in webhook_url.lower():
                payload = {
                    'content': f"**{title}**\n\n{message}",
                    'username': 'Berlin Appointment Monitor'
                }
            elif 'slack' in webhook_url.lower():
                payload = {
                    'text': f"*{title}*\n\n{message}",
                    'username': 'Berlin Appointment Monitor'
                }
            else:
                # Generic webhook format
                payload = {
                    'title': title,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }
            
            response = requests.post(webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info("Webhook notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {str(e)}")
            return False