# AI Startup

An autonomous system that continuously improves its own codebase using AI agents.

## Features

- **Autonomous Code Improvement**: AI agents analyze and enhance the codebase
- **Continuous Learning**: System learns from its own improvements
- **Self-Maintaining**: Automatically updates dependencies and documentation
- **Real-time Monitoring**: Tracks system performance and improvements

## Architecture

The system consists of several key components:

1. **AI Agents**:
   - Founder Agent: Strategic planning and high-level improvements
   - Developer Agent: Code implementation and technical improvements

2. **Core Components**:
   - System Orchestrator: Coordinates the improvement cycle
   - Code Manager: Handles code changes and version control
   - Rate Limiter: Manages API usage and resource allocation
   - Observability: Monitors system performance and improvements

3. **Infrastructure**:
   - FastAPI backend
   - SQLite database
   - GitHub integration
   - Gemini API for AI capabilities

## Development

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account
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
   GITHUB_TOKEN=your_token_here
   ```

### Running the Application

1. Make sure you're in the virtual environment (you should see `(venv)` in your prompt)

2. Start the development server:
   ```bash
   python -m src.main
   ```

3. The server will be available at `http://localhost:8000`

### Testing

1. Make sure you're in the virtual environment and the package is installed in development mode

2. Run all tests:
   ```bash
   pytest
   ```

3. Run tests with coverage:
   ```bash
   pytest --cov=src
   ```

4. Run specific test file:
   ```bash
   pytest tests/test_repo_reader.py
   ```

### Development Workflow

1. Make your changes in the `src` directory
2. Run tests to ensure everything works
3. Commit your changes
4. The system will automatically analyze and improve the codebase

### Code Quality

The project uses several tools to maintain code quality:

1. **Black**: Code formatting
   ```bash
   black src tests
   ```

2. **isort**: Import sorting
   ```bash
   isort src tests
   ```

3. **flake8**: Linting
   ```bash
   flake8 src tests
   ```

4. **mypy**: Type checking
   ```bash
   mypy src
   ```

### Troubleshooting

#### ModuleNotFoundError: No module named 'ai_startup'

This error occurs when the package isn't installed in development mode. To fix:

1. Make sure you're in the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

3. Verify the installation:
   ```bash
   pip list | grep ai-startup
   ```

#### Other Common Issues

- **Package not found**: Make sure you're in the correct directory and the virtual environment is activated

- **API errors**: Check your `.env` file and make sure your API keys are correct

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 