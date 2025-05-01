# Deployment Guide

This guide provides detailed instructions for deploying the AI Startup Self-Improvement System in a production environment.

## Prerequisites

- Linux server (Ubuntu 20.04 or later recommended)
- Python 3.8 or later
- Git
- Systemd (for service management)
- Cron (for scheduling)

## Server Setup

1. Create a dedicated user:
   ```bash
   sudo useradd -m -s /bin/bash ai-startup
   sudo usermod -aG sudo ai-startup
   ```

2. Set up the application directory:
   ```bash
   sudo mkdir -p /opt/ai-startup
   sudo chown ai-startup:ai-startup /opt/ai-startup
   ```

## Deployment Steps

1. Clone the repository:
   ```bash
   sudo -u ai-startup git clone https://github.com/yourusername/ai-startup.git /opt/ai-startup
   ```

2. Set up the virtual environment:
   ```bash
   cd /opt/ai-startup
   sudo -u ai-startup python -m venv venv
   sudo -u ai-startup ./venv/bin/pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   sudo -u ai-startup cp .env.example .env
   sudo -u ai-startup nano .env  # Edit with your API keys
   ```

4. Set up the systemd service:
   ```bash
   sudo cp ai-startup.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable ai-startup
   sudo systemctl start ai-startup
   ```

5. Configure the daily cron job:
   ```bash
   sudo -u ai-startup crontab -e
   # Add this line to run daily at 2 AM
   0 2 * * * /opt/ai-startup/venv/bin/python /opt/ai-startup/src/main.py >> /opt/ai-startup/logs/cron.log 2>&1
   ```

## Directory Structure

```
/opt/ai-startup/
├── src/              # Source code
├── venv/             # Virtual environment
├── logs/             # Application logs
├── backups/          # System backups
├── .env              # Environment variables
└── requirements.txt  # Python dependencies
```

## Logging and Monitoring

1. Check systemd service status:
   ```bash
   sudo systemctl status ai-startup
   ```

2. View application logs:
   ```bash
   sudo -u ai-startup tail -f /opt/ai-startup/logs/app.log
   ```

3. View cron logs:
   ```bash
   sudo -u ai-startup tail -f /opt/ai-startup/logs/cron.log
   ```

## Backup and Restore

1. Backups are automatically created in `/opt/ai-startup/backups/`
2. Each backup is timestamped
3. The system maintains the last 7 days of backups

## Security Considerations

1. The `ai-startup` user should have minimal permissions
2. API keys should be stored securely in `.env`
3. Regular security updates should be applied
4. Monitor rate limits and API usage

## Troubleshooting

1. Check service status:
   ```bash
   sudo systemctl status ai-startup
   ```

2. View service logs:
   ```bash
   sudo journalctl -u ai-startup
   ```

3. Check cron job:
   ```bash
   sudo -u ai-startup crontab -l
   ```

4. Verify API keys:
   ```bash
   sudo -u ai-startup cat /opt/ai-startup/.env
   ```

## Updates

To update the system:

1. Pull the latest changes:
   ```bash
   cd /opt/ai-startup
   sudo -u ai-startup git pull
   ```

2. Update dependencies:
   ```bash
   sudo -u ai-startup ./venv/bin/pip install -r requirements.txt
   ```

3. Restart the service:
   ```bash
   sudo systemctl restart ai-startup
   ``` 