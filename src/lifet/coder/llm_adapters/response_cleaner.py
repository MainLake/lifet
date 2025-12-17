from abc import ABC, abstractmethod
import re

class ResponseCleanerProtocol(ABC):
    @abstractmethod
    def clean(self, response: str) -> str:
        """Cleans the raw response from the LLM."""
        pass

class GeminiJSONCleaner(ResponseCleanerProtocol):
    def clean(self, response: str) -> str:
        """
        Cleans a string that should contain a JSON object,
        removing markdown and fixing common formatting errors.
        """
        clean_text = response.strip()

        # 1. Remove Markdown blocks
        match = re.search(r"```(?:json)?\s*(.*)\s*```", clean_text, re.DOTALL)
        if match:
            clean_text = match.group(1)
        
        clean_text = clean_text.strip()

        # 2. Fix escaped single quotes
        clean_text = clean_text.replace(r"\'", "'")

        # 3. Fix doubly escaped double quotes
        clean_text = clean_text.replace(r'\\"', r'"')

        return clean_text
