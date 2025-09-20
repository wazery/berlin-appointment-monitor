# Berlin Service Appointment Monitor

A GitHub Actions-powered tool that monitors the Berlin service website for available appointments and sends notifications when appointments become available.

## 🌟 Features

- **Automated Monitoring**: Runs every 5 minutes during business hours using GitHub Actions
- **Multiple Notification Methods**: 
  - GitHub Issues (automatic)
  - **Mobile Push Notifications** (Pushover, Pushbullet, ntfy.sh)
  - Email notifications
  - Webhook notifications (Discord, Slack, etc.)
- **Zero Infrastructure Costs**: Runs entirely on GitHub's servers
- **Easy Setup**: Just configure secrets and the workflow starts running

## 🚀 Quick Setup

### 1. Fork or Clone This Repository

```bash
git clone https://github.com/your-username/berlin-appointment-monitor.git
cd berlin-appointment-monitor
```

### 2. Configure Secrets

Go to your repository Settings → Secrets and variables → Actions, and add these optional secrets:

#### Mobile Push Notifications (Recommended - Easy Setup)

**Option 1: Pushover (Recommended)**
- `PUSHOVER_TOKEN`: Your Pushover app token ([create app](https://pushover.net/apps/build))
- `PUSHOVER_USER`: Your Pushover user key ([find here](https://pushover.net/))

**Option 2: Pushbullet**
- `PUSHBULLET_TOKEN`: Your Pushbullet access token ([get token](https://www.pushbullet.com/#settings/account))

**Option 3: ntfy.sh (Free, No Account)**
- `NTFY_TOPIC`: Your unique topic name (e.g., `berlin-appointments-yourname`)

#### Email Notifications (Optional)
- `NOTIFICATION_EMAIL`: Your Gmail address
- `EMAIL_PASSWORD`: Your Gmail app password ([how to create](https://support.google.com/accounts/answer/185833))

#### Webhook Notifications (Optional)
- `WEBHOOK_URL`: Your Discord/Slack webhook URL

#### GitHub Issues (Automatic)
- No setup required! The workflow automatically creates issues using `GITHUB_TOKEN`

### 3. Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. Enable workflows if prompted
3. The monitor will start running automatically based on the cron schedule

### 4. Manual Testing

You can manually trigger the monitor:
1. Go to Actions → "Berlin Service Appointment Monitor"
2. Click "Run workflow"
3. Check the results in the workflow logs

## 📱 Mobile Push Notification Setup

### Pushover (Recommended - $5 one-time)
1. Download the Pushover app on your phone
2. Create account at [pushover.net](https://pushover.net/)
3. Create a new app at [pushover.net/apps/build](https://pushover.net/apps/build)
4. Add `PUSHOVER_TOKEN` (app token) and `PUSHOVER_USER` (user key) to GitHub Secrets

### Pushbullet (Free tier available)
1. Download the Pushbullet app on your phone
2. Create account at [pushbullet.com](https://www.pushbullet.com/)
3. Get your access token from [pushbullet.com/#settings/account](https://www.pushbullet.com/#settings/account)
4. Add `PUSHBULLET_TOKEN` to GitHub Secrets

### ntfy.sh (Completely Free)
1. Download the ntfy app on your phone
2. Choose a unique topic name (e.g., `berlin-appointments-yourname123`)
3. Subscribe to the topic in the app: `ntfy.sh/your-topic-name`
4. Add `NTFY_TOPIC` (your topic name) to GitHub Secrets
5. No account needed!

## 📋 How It Works

1. **GitHub Actions** runs the monitor on a schedule (every 5 minutes during business hours)
2. **Web Scraper** checks https://service.berlin.de/dienstleistung/324591/ for appointments
3. **Notification System** sends alerts through your configured channels when appointments are found
4. **GitHub Issues** are created automatically for each appointment alert

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CHECK_INTERVAL` | Check interval in seconds | 300 | No |
| `REQUEST_TIMEOUT` | HTTP request timeout | 30 | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `PUSHOVER_TOKEN` | Pushover app token | - | No |
| `PUSHOVER_USER` | Pushover user key | - | No |
| `PUSHBULLET_TOKEN` | Pushbullet access token | - | No |
| `NTFY_TOPIC` | ntfy.sh topic name | - | No |
| `NOTIFICATION_EMAIL` | Email for notifications | - | No |
| `EMAIL_PASSWORD` | Email app password | - | No |
| `WEBHOOK_URL` | Webhook URL for notifications | - | No |

### Cron Schedule

The default schedule runs every 5 minutes during business hours (8 AM - 6 PM, Monday-Friday, Berlin time):

```yaml
schedule:
  - cron: '*/5 8-18 * * 1-5'
```

You can modify this in `.github/workflows/monitor.yml` to change the frequency.

## 📁 Project Structure

```
berlin-appointment-monitor/
├── .github/
│   ├── workflows/
│   │   └── monitor.yml          # GitHub Actions workflow
│   └── copilot-instructions.md  # AI assistant instructions
├── src/
│   ├── main.py                  # Main application entry point
│   ├── scraper.py              # Web scraping logic
│   ├── notifier.py             # Notification handling
│   └── config.py               # Configuration management
├── logs/                       # Log files (created automatically)
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🔍 Monitoring and Logs

- **GitHub Actions Logs**: Check the "Actions" tab for detailed execution logs
- **GitHub Issues**: Automatic appointment alerts are created as issues
- **Workflow Artifacts**: Logs are uploaded as artifacts if the workflow fails

## 🛠️ Local Development

### Prerequisites
- Python 3.9+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/your-username/berlin-appointment-monitor.git
cd berlin-appointment-monitor

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Run the monitor
python src/main.py
```

### Testing
```bash
# Install test dependencies
pip install pytest pytest-mock requests-mock

# Run tests
pytest tests/
```

## 📧 Notification Examples

### Mobile Push Notification (Pushover)
- **Title**: "🎉 Berlin Service Appointments Available!"
- **Message**: Detailed appointment information with location and direct links
- **Priority**: High priority with attention-grabbing sound
- **Instant delivery** to your phone

### Mobile Push Notification (ntfy.sh)
- **Title**: "🎉 Berlin Service Appointments Available!"
- **Message**: Rich notification with appointment details
- **Tags**: `appointment`, `berlin`
- **Free service**, no account required

### GitHub Issue
- **Title**: "🎉 Berlin Service Appointments Available!"
- **Labels**: `appointment-alert`, `automated`
- **Body**: Detailed appointment information with direct links

### Email
- **Subject**: "🎉 Berlin Service Appointments Available!"
- **Body**: Formatted appointment details with timestamps

### Discord/Slack Webhook
- **Message**: Formatted notification with appointment details

## ⚡ Customization

### Different Service
To monitor a different Berlin service, update the URL in `src/scraper.py`:
```python
self.base_url = "https://service.berlin.de/dienstleistung/YOUR_SERVICE_ID/"
```

### Check Frequency
Modify the cron schedule in `.github/workflows/monitor.yml`:
```yaml
# Every 2 minutes during extended hours
- cron: '*/2 7-20 * * 1-6'
```

### Additional Notifications
Add new notification methods in `src/notifier.py` by implementing new `_send_*` methods.

## 🔒 Privacy and Security

- **No Personal Data Storage**: The monitor only checks public appointment availability
- **Secure Credentials**: All sensitive data is stored in GitHub Secrets
- **Rate Limiting**: Built-in delays to avoid overloading the Berlin service website
- **Open Source**: Full transparency in how the monitor works

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Wiki**: Check the repository wiki for additional documentation

## ⚠️ Disclaimer

This tool is for personal use only. Please respect the Berlin service website's terms of service and avoid excessive requests. The monitor includes built-in rate limiting to be respectful of the service.

---

**Happy appointment hunting! 🎯**