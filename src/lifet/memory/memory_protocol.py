from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Literal

class MemoryInteraction(BaseModel):
    """Represents a single interaction in the memory."""
    role: Literal["user", "assistant", "system", "tool"]
    content: str

class MemoryProtocol(ABC):
    
    @abstractmethod
    def save_memory(self, interaction: MemoryInteraction):
        """Saves a single interaction to the memory."""
        pass

    @abstractmethod
    def get_memory(self) -> str:
        """
        Retrieves the entire memory context as a single string,
        formatted for inclusion in a prompt.
        """
        pass

