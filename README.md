# AI Startup Self-Improvement System

An autonomous system that continuously improves its own codebase using AI agents.

## Features

- Autonomous code analysis and improvement
- Safety checks and validation
- Pull request-based changes
- Rate limiting for API calls
- Comprehensive logging and observability

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-startup.git
   cd ai-startup
   ```

2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Update your `.env` file with API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GITHUB_TOKEN=your_github_token
   ```

4. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. Run the development server:
   ```bash
   python src/main.py
   ```

## Production Deployment

1. Clone the repository to your server:
   ```bash
   git clone https://github.com/yourusername/ai-startup.git
   cd ai-startup
   ```

2. Run the deployment script:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. Set up the daily cron job:
   ```bash
   # Edit crontab
   crontab -e
   
   # Add this line to run daily at 2 AM
   0 2 * * * /opt/ai-startup/venv/bin/python /opt/ai-startup/src/main.py >> /opt/ai-startup/logs/cron.log 2>&1
   ```

## Project Structure

```
ai-startup/
├── src/
│   ├── agents/
│   │   ├── base.py
│   │   ├── founder.py
│   │   ├── developer.py
│   │   └── __init__.py
│   ├── code_manager.py
│   ├── safety_checker.py
│   ├── rate_limits.py
│   ├── observability.py
│   └── orchestrator.py
├── logs/
├── backups/
├── requirements.txt
├── setup.sh
├── deploy.sh
├── ai-startup.service
└── .env
```

## Configuration

- Rate limits are configured in `src/rate_limits.py`
- API keys are stored in `.env`
- Logs are stored in `logs/` directory
- Backups are stored in `backups/` directory

## Monitoring

- Check logs in `logs/` directory
- Monitor GitHub repository for pull requests
- Review observability logs for system improvements

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License 