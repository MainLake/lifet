from typing import List
from lifet.memory.memory_protocol import MemoryProtocol, MemoryInteraction

class InMemoryMemory(MemoryProtocol):
    """
    An in-memory implementation of the MemoryProtocol that stores interactions
    in a simple list, with a token limit to manage context window size.
    """
    def __init__(self, max_token_count: int = 4096):
        self.interactions: List[MemoryInteraction] = []
        self.max_token_count = max_token_count

    def save_memory(self, interaction: MemoryInteraction):
        """Saves a single interaction to the in-memory list."""
        self.interactions.append(interaction)
        self.trim_memory()

    def get_memory(self) -> str:
        """
        Retrieves the memory context as a single string, formatted for a prompt.
        """
        formatted_memory = []
        for interaction in self.interactions:
            role_display = ""
            if interaction.role == "tool":
                role_display = "[TOOL_RESULT]"
            else:
                role_display = f"[{interaction.role.upper()}]"
            
            formatted_memory.append(f"{role_display}\n{interaction.content}")
        return "\n".join(formatted_memory)

    def trim_memory(self):
        """
        Removes the oldest interactions if the total token count exceeds the limit.
        A rough estimation of 1 token ~= 4 characters is used.
        """
        total_chars = sum(len(i.content) for i in self.interactions)
        
        while total_chars > self.max_token_count * 3.5 and len(self.interactions) > 1:
            removed_interaction = self.interactions.pop(0)
            total_chars -= len(removed_interaction.content)

