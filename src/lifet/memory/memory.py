from typing import List
from lifet.memory.memory_protocol import MemoryProtocol, MemoryInteraction

class InMemoryMemory(MemoryProtocol):
    """
    An in-memory implementation of the MemoryProtocol that stores interactions
    in a simple list.
    """
    def __init__(self):
        self.interactions: List[MemoryInteraction] = []

    def save_memory(self, interaction: MemoryInteraction):
        """Saves a single interaction to the in-memory list."""
        self.interactions.append(interaction)

    def get_memory(self) -> str:
        """
        Retrieves the entire memory context as a single, token-efficient string.
        """
        formatted_memory = []
        for interaction in self.interactions:
            formatted_memory.append(f"[{interaction.role.upper()}]\n{interaction.content}")
        return "\n".join(formatted_memory)

