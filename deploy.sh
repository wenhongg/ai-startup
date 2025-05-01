#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p backups

# Set up systemd service (Linux only)
if [ "$(uname)" == "Linux" ]; then
    echo "Setting up systemd service..."
    sudo cp ai-startup.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable ai-startup
    sudo systemctl start ai-startup
    echo "Service installed and started. Check status with: sudo systemctl status ai-startup"
fi

echo "Deployment complete! Don't forget to:"
echo "1. Update your .env file with API keys"
echo "2. Configure your system's cron job for daily runs"
echo "3. Monitor logs in the logs/ directory" 