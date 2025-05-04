from ..agents.base import BaseAgent
from ..config import settings
from .code_reader import CodeReader
from typing import Dict, Any, List, Tuple, Optional

class DeveloperAI(BaseAgent):
    def __init__(self, code_reader: CodeReader):
        super().__init__()
        self.temperature = settings.temperature_developer
        self.system_prompt = self._load_prompt("developer.txt")
        self.code_reader = code_reader

    def review_proposal(self, proposal: str) -> Tuple[str, str, List[str]]:
        """
        Review the proposal and create a plan for implementation.
        
        Args:
            proposal: The improvement proposal from the founder
            
        Returns:
            Tuple containing:
            - PR title: A clear, concise title for the pull request
            - PR description: Detailed description of the changes
            - files_to_change: List of file paths that need to be modified
        """
        # Get code summaries
        code_summaries = self.code_reader.get_code_summaries()
        
        # Format the prompt with all parameters
        prompt = f"""
Review the following improvement proposal and create a detailed implementation plan:

Proposal:
{proposal}

Current codebase summaries:
{code_summaries}

Please provide:
1. A clear, concise title for the pull request (max 50 characters)
2. A detailed description of the changes to be made, including:
   - What changes will be made
   - Why these changes are beneficial
   - Any potential impacts
   - Testing that will be done
3. A list of specific files that need to be modified, with a brief explanation for each

Format your response as follows:
TITLE: [your title here]
DESCRIPTION: [your description here]
FILES:
- file1.py: [reason for change]
- file2.py: [reason for change]
...
"""
        response = self.generate_response(prompt)
        
        # Parse the response
        title = ""
        description = ""
        files_to_change = []
        
        current_section = None
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('TITLE:'):
                current_section = 'title'
                title = line[6:].strip()
            elif line.startswith('DESCRIPTION:'):
                current_section = 'description'
                description = line[12:].strip()
            elif line.startswith('FILES:'):
                current_section = 'files'
            elif current_section == 'description':
                description += '\n' + line
            elif current_section == 'files' and line.startswith('-'):
                # Extract file path and reason
                parts = line[1:].split(':', 1)
                if len(parts) == 2:
                    file_path = parts[0].strip()
                    files_to_change.append(file_path)
        
        return title, description, files_to_change

    def implement_changes(self, proposal: str) -> Tuple[Dict[str, Any], str, str]:
        """Implement the changes and generate pull request details
        Returns a tuple of (changes, title, description)
        """
        # First review the proposal to get the plan
        title, description, files_to_change = self.review_proposal(proposal)
        
        # Process each file
        changes = {}
        for file_path in files_to_change:
            # Get current file contents
            current_content = self.code_reader.read_file(file_path)
            
            # Remove ` characters from file_path if they exist at start or end
            file_path = file_path.strip('`')
            
            # Format the prompt for this file
            prompt = f"""Based on the following pull request details and current file contents, 
update the file to implement the requested changes.

Pull Request Title: {title}
Pull Request Description: {description}

Current filename: {file_path}
Current file contents:
{current_content}

Please provide the complete updated file contents, maintaining the same file structure and format.
For each file, return ONLY the complete code that should replace the existing file. Do not include any explanations, comments about the changes, or markdown formatting. Strictly no markdown formatting."""
            
            # Get the updated file contents
            updated_content = self.generate_response(prompt)
            
            # Remove lines that start with ``` at beginning or end
            lines = updated_content.split('\n')
            while lines and lines[0].strip().startswith('```'):
                lines.pop(0)
            while lines and lines[-1].strip().startswith('```'):
                lines.pop()
            updated_content = '\n'.join(lines)
            
            changes[file_path] = updated_content
        
        return changes, title, description