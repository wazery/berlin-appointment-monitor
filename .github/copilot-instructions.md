<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Berlin Service Appointment Monitor

This project monitors the Berlin service website for available appointments using GitHub Actions on a cron schedule. When appointments become available, it sends notifications via GitHub Issues, email, or webhooks.

## Project Structure
- `.github/workflows/monitor.yml` - GitHub Actions workflow for scheduled monitoring
- `src/main.py` - Main application entry point
- `src/scraper.py` - Web scraping module for Berlin service website
- `src/notifier.py` - Notification handling (GitHub Issues, email, webhooks)
- `src/config.py` - Configuration management
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation

## Key Features
- GitHub Actions workflow with cron scheduling
- Web scraping of https://service.berlin.de/dienstleistung/324591/
- Automated appointment checking every few minutes
- Multiple notification methods:
  - GitHub Issues (automatic)
  - Mobile push notifications (Pushover, Pushbullet, ntfy.sh)
  - Email notifications
  - Webhook notifications (Discord, Slack, etc.)
- Environment variables for configuration
- No infrastructure costs (runs on GitHub's servers)

## Development Guidelines
- Use Python 3.9+ (GitHub Actions runner compatibility)
- Follow PEP 8 style guidelines
- Include error handling for network requests
- Use GitHub Secrets for sensitive configuration
- Implement proper logging for workflow debugging
- Use GitHub Issues for appointment notifications by default