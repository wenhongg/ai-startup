# AI Self-Improvement System

This project implements an AI system that can analyze and improve its own codebase. The system consists of two AI agents:

1. **Founder AI**: Analyzes the system and proposes improvements
2. **Developer AI**: Reviews proposals and implements changes

## Project Structure

```
ai-startup/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── founder.py
│   │   └── developer.py
│   ├── code_manager.py
│   ├── config.py
│   ├── orchestrator.py
│   └── safety_checker.py
├── prompts/
│   ├── founder.txt
│   └── developer.txt
├── requirements.txt
└── README.md
```

## Key Components

### Agents
- `src/agents/base.py`: Base class for AI agents with common functionality
- `src/agents/founder.py`: Founder AI implementation
- `src/agents/developer.py`: Developer AI implementation

### Core System
- `src/code_manager.py`: Manages code changes and pull requests
- `src/safety_checker.py`: Validates changes and ensures system safety
- `src/orchestrator.py`: Coordinates the improvement cycle

### Configuration
- `src/config.py`: System configuration and settings
- `prompts/`: Directory containing AI agent prompts

## Workflow

1. **Analysis**: Founder AI analyzes the system
2. **Proposal**: Founder AI generates improvement proposals
3. **Review**: Developer AI reviews and plans implementation
4. **Safety Check**: System validates proposed changes
5. **Implementation**: Developer AI implements changes
6. **Pull Request**: Changes are submitted as pull requests for review

## Safety Features

- Protected files and patterns
- Syntax validation
- Dangerous operation detection
- Backup and restore functionality
- Multiple safety checks before implementation

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the system in `src/config.py`

3. Run the improvement cycle:
   ```python
   from src.orchestrator import SystemOrchestrator
   
   orchestrator = SystemOrchestrator()
   result = await orchestrator.improvement_cycle()
   ```

## Safety Checks

The system includes multiple safety checks:

1. **Protected Files**: Core system files that must not be modified
2. **Protected Patterns**: Critical code patterns that must be preserved
3. **Syntax Validation**: Ensures all changes are valid Python code
4. **Dangerous Operations**: Prevents unsafe operations like:
   - Direct file system access
   - Network operations
   - System commands
   - Dynamic code execution

## Contributing

All changes must go through the pull request process, where:
1. The AI system proposes changes
2. Changes are validated by the safety checker
3. Pull requests are created for manual review
4. Changes are only merged after approval

## License

MIT License 

## Logs

```
logs/
├── proposal_20240315.txt
├── implementation_plan_20240315.txt
├── proposal_20240316.txt
└── implementation_plan_20240316.txt
``` 