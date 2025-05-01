#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "OPENAI_API_KEY=" > .env
    echo "GITHUB_TOKEN=" >> .env
    echo "Please update the .env file with your API keys"
fi

# Create necessary directories
mkdir -p logs
mkdir -p backups

echo "Setup complete! Don't forget to:"
echo "1. Update your .env file with API keys"
echo "2. Activate the virtual environment with: source venv/bin/activate"
echo "3. Run the development server with: python src/main.py" 