# AI Startup

An autonomous system that continuously improves its own codebase using AI agents.

## Features

- **Autonomous Code Improvement**: AI agents analyze and enhance the codebase
- **Continuous Learning**: System learns from its own improvements
- **Self-Maintaining**: Automatically updates dependencies and documentation
- **Real-time Monitoring**: Tracks system performance and improvements
- **GitHub Integration**: Direct integration with GitHub for code management
- **Rate Limiting**: Smart management of API usage for both GitHub and AI services

## Architecture

The system consists of several key components:

1. **AI Agents**:
   - Founder Agent: Strategic planning and high-level improvements
   - Developer Agent: Code implementation and technical improvements
   - Code Reader: Specialized in reading and summarizing code files

2. **Core Components**:
   - System Orchestrator: Coordinates the improvement cycle
   - Code Manager: Handles GitHub operations (branches, pull requests, file changes)
   - Rate Limiter: Manages API usage and resource allocation
   - Repo Reader: Handles GitHub repository access and file operations

3. **Infrastructure**:
   - FastAPI backend
   - GitHub API integration
   - Gemini API for AI capabilities
   - Environment-based configuration

## Development

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account with a Personal Access Token (with `repo` permissions)
- A Gemini API key (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-startup.git
   cd ai-startup
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   # Install with all dependencies including development tools
   pip install -e ".[dev]"
   ```

4. Create a `.env` file with your API keys:
   ```bash
   # Get your API key from https://makersuite.google.com/app/apikey
   GEMINI_API_KEY=your_key_here
   
   # Create a GitHub Personal Access Token with 'repo' permissions
   GITHUB_TOKEN=your_token_here
   
   # Optional: Configure other settings
   GEMINI_RATE_LIMIT=60
   GITHUB_RATE_LIMIT=5000
   LOG_LEVEL=INFO
   ```

### Running the Application

1. Start the application:
   ```bash
   python src/main.py
   ```

2. The system will:
   - Initialize all components
   - Start the improvement cycle
   - Create pull requests for approved changes
   - Monitor and log all operations

### Testing

Run the test suite:
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_code_manager.py -v
```

## How It Works

1. **Improvement Cycle**:
   - Code Reader summarizes the current codebase
   - Founder Agent analyzes and proposes improvements
   - Developer Agent reviews and implements changes
   - Code Manager creates pull requests on GitHub
   - System Orchestrator coordinates the entire process

2. **Code Management**:
   - Automatic branch creation
   - File modification and creation
   - Pull request generation
   - Rate-limited API calls

3. **Safety Features**:
   - Protected code patterns
   - Rate limiting
   - Error handling
   - Logging and monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details 