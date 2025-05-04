```python
from ..agents.base import BaseAgent
from ..config import settings
from .code_reader import CodeReader
from ..models.proposal import Proposal, ProposalParseError
import re

class FounderAI(BaseAgent):
    def __init__(self, code_reader: CodeReader):
        super().__init__()
        self.temperature = settings.temperature_founder
        self.code_reader = code_reader
        self.system_prompt = self._load_prompt("founder.txt")
        self._cached_proposal = None

    def _parse_proposal(self, proposal_text: str) -> Proposal:
        """Parses the LLM output and extracts proposal details.

        Args:
            proposal_text: The raw text output from the LLM.

        Returns:
            A Proposal object containing the parsed data.

        Raises:
            ProposalParseError: If the parsing fails or the output is invalid.
        """
        try:
            area_match = re.search(r"Area for Improvement:\s*(.*)", proposal_text, re.DOTALL)
            rationale_match = re.search(r"Rationale:\s*(.*)", proposal_text, re.DOTALL)
            changes_match = re.search(r"Suggested Changes:\s*(.*)", proposal_text, re.DOTALL)
            risks_match = re.search(r"Potential Risks:\s*(.*)", proposal_text, re.DOTALL)
            effort_match = re.search(r"Effort Level:\s*(.*)", proposal_text, re.DOTALL)

            area_for_improvement = area_match.group(1).strip() if area_match else ""
            rationale = rationale_match.group(1).strip() if rationale_match else ""
            suggested_changes = changes_match.group(1).strip() if changes_match else ""
            risks = risks_match.group(1).strip() if risks_match else ""
            effort_level = effort_match.group(1).strip() if effort_match else ""
            
            proposal_data = {
                "area_for_improvement": area_for_improvement,
                "rationale": rationale,
                "suggested_changes": suggested_changes,
                "risks": risks,
                "effort_level": effort_level,
            }

            proposal = Proposal(**proposal_data)
            return proposal

        except Exception as e:
            raise ProposalParseError(f"Failed to parse proposal: {e}. Output:\n{proposal_text}")


    def generate_proposal(self, product_summaries: str) -> Proposal:
        """Generate an improvement proposal based on the product information.

        Args:
            product_summaries: A comprehensive summary of the product codebase

        Returns:
            A detailed improvement proposal
        """
        # Check cache first
        if self._cached_proposal is not None:
            return self._cached_proposal

        prompt = f"""{self.system_prompt}

Product Information:
{product_summaries}

Based on the above information, please analyze the current state and propose improvements.
Focus on a small area to improve, and make sure it's something that will be useful to the user.
Provide the output in the following format:

Area for Improvement: <Specific area for improvement>
Rationale: <Why this area is important, detailing the benefit or impact>
Suggested Changes: <How the change can be achieved, providing suggested changes>
Potential Risks: <Potential risks associated with the improvement>
Effort Level: <Estimated level of effort (e.g., Low, Medium, High)>
"""

        proposal_text = self.generate_response(prompt=prompt)

        try:
            proposal = self._parse_proposal(proposal_text)
            self._cached_proposal = proposal
            return proposal
        except ProposalParseError as e:
            print(f"Proposal parsing failed: {e}")
            self._cached_proposal = None  # Reset cache on parsing failure
            return None

    def get_cached_proposal(self) -> Proposal:
        """Get the cached proposal if available.

        Returns:
            The cached proposal, or None if no proposal has been generated yet
        """
        return self._cached_proposal

    def reset(self):
        """Clear the cached proposal."""
        self._cached_proposal = None
```
