# Deployment Guide

This guide explains how to deploy the AI Self-Improvement System with daily improvement cycles.

## Prerequisites

- Python 3.8+
- Git
- OpenAI API key
- GitHub repository access
- Server/VM with cron or similar scheduling capability

## Setup Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd ai-startup
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   GITHUB_TOKEN=your_github_token_here
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ```

5. **Configure GitHub Access**
   - Generate a GitHub Personal Access Token with `repo` scope
   - Add the token to your `.env` file
   - Ensure the repository is properly configured for pull requests

## Setting Up Daily Improvement Cycles

### Option 1: Using Cron (Linux/Mac)

1. Create a script to run the improvement cycle:
   ```bash
   #!/bin/bash
   cd /path/to/ai-startup
   source venv/bin/activate
   python -c "from src.orchestrator import SystemOrchestrator; import asyncio; asyncio.run(SystemOrchestrator().improvement_cycle())"
   ```

2. Make the script executable:
   ```bash
   chmod +x run_improvement_cycle.sh
   ```

3. Add to crontab:
   ```bash
   # Run at 2 AM daily
   0 2 * * * /path/to/run_improvement_cycle.sh >> /path/to/improvement_logs.log 2>&1
   ```

### Option 2: Using Windows Task Scheduler

1. Create a batch script:
   ```batch
   @echo off
   cd C:\path\to\ai-startup
   call venv\Scripts\activate
   python -c "from src.orchestrator import SystemOrchestrator; import asyncio; asyncio.run(SystemOrchestrator().improvement_cycle())"
   ```

2. Create a scheduled task:
   - Open Task Scheduler
   - Create Basic Task
   - Set trigger to daily at 2 AM
   - Action: Start a program
   - Program: `C:\path\to\run_improvement_cycle.bat`

### Option 3: Using Docker

1. Create a Dockerfile:
   ```dockerfile
   FROM python:3.8-slim

   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt

   CMD ["python", "-c", "from src.orchestrator import SystemOrchestrator; import asyncio; asyncio.run(SystemOrchestrator().improvement_cycle())"]
   ```

2. Build and run with cron:
   ```bash
   docker build -t ai-improvement .
   docker run -d \
     --env-file .env \
     -v /path/to/logs:/app/logs \
     ai-improvement
   ```

## Monitoring and Maintenance

1. **Logs**
   - System logs are stored in `logs/` directory
   - Each improvement cycle creates a detailed log entry
   - Pull request history is maintained in GitHub

2. **Alerting**
   - Set up monitoring for:
     - Failed improvement cycles
     - Pull request creation failures
     - Safety check violations
     - API quota limits

3. **Backup**
   - Regular backups of:
     - Repository state
     - Configuration files
     - Log files
     - Environment variables

## Security Considerations

1. **API Keys**
   - Store API keys securely
   - Use environment variables
   - Rotate keys regularly
   - Limit key permissions

2. **Repository Access**
   - Use least-privilege principle
   - Limit write access to necessary files
   - Monitor pull request activity
   - Review all changes before merging

3. **System Access**
   - Secure the deployment server
   - Regular security updates
   - Monitor system resources
   - Set up firewall rules

## Troubleshooting

1. **Common Issues**
   - API quota exceeded
   - GitHub rate limits
   - Permission issues
   - Environment configuration problems

2. **Debugging**
   - Check logs in `logs/` directory
   - Review GitHub pull request history
   - Verify environment variables
   - Test API connectivity

3. **Recovery**
   - Restore from backup if needed
   - Reset environment variables
   - Clear temporary files
   - Restart the service

## Scaling Considerations

1. **Resource Usage**
   - Monitor CPU and memory usage
   - Adjust scheduling based on load
   - Consider parallel processing
   - Optimize API calls

2. **Rate Limits**
   - Implement rate limiting
   - Queue improvement cycles
   - Handle API errors gracefully
   - Implement retry logic

3. **Storage**
   - Monitor log file growth
   - Implement log rotation
   - Clean up old backups
   - Archive completed cycles

## Best Practices

1. **Regular Maintenance**
   - Review pull requests daily
   - Monitor system performance
   - Update dependencies
   - Clean up old branches

2. **Documentation**
   - Keep README_ai.md updated
   - Document significant changes
   - Maintain deployment notes
   - Track known issues

3. **Testing**
   - Test in staging environment
   - Verify safety checks
   - Monitor improvement quality
   - Validate pull requests

Remember: While the system runs automatically, human oversight is crucial. Regular review of pull requests and system performance is essential for maintaining system integrity and quality. 