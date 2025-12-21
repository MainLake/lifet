from typing import List
from lifet.memory.memory_protocol import MemoryProtocol, MemoryInteraction
from lifet.coder.llm_adapters.llm_adapter_protocol import LLMAdapterProtocol, RequestLLM

class SummarizingMemory(MemoryProtocol):
    """
    A memory implementation that summarizes the conversation to keep the context
    window small.
    """
    def __init__(self, llm_adapter: LLMAdapterProtocol, max_buffer_size: int = 10):
        self.llm_adapter = llm_adapter
        self.max_buffer_size = max_buffer_size
        self.interactions: List[MemoryInteraction] = []
        self.summary: str = ""

    def save_memory(self, interaction: MemoryInteraction):
        """Saves a single interaction and summarizes if the buffer is full."""
        self.interactions.append(interaction)
        
        if len(self.interactions) > self.max_buffer_size:
            self.summarize()

    def get_memory(self) -> str:
        """
        Retrieves the memory context, including the summary and recent interactions.
        """
        formatted_memory = []
        if self.summary:
            formatted_memory.append(f"[SUMMARY]\n{self.summary}")
            
        for interaction in self.interactions:
            formatted_memory.append(f"[{interaction.role.upper()}]\n{interaction.content}")
            
        return "\n\n".join(formatted_memory)

    def summarize(self):
        """Summarizes the oldest interactions in the buffer."""
        if not self.interactions:
            return

        # Take the oldest interactions to summarize
        interactions_to_summarize = self.interactions[:-self.max_buffer_size//2]
        self.interactions = self.interactions[-self.max_buffer_size//2:]

        # Format the interactions for the summarization prompt
        conversation = "\n".join([f"{i.role}: {i.content}" for i in interactions_to_summarize])
        
        prompt = f"Summarize the following conversation:\n\n{conversation}"
        
        # Call the LLM to summarize
        request = RequestLLM(
            request_user=prompt, 
            request_system_data="You are a summarization expert.",
            json_schema={},
            agent_persona=None,
            katas_rules=None
        )
        response = self.llm_adapter.generate_content(request)
        
        if response and response.response:
            # Prepend the new summary to the existing summary
            self.summary = f"{response.response}\n{self.summary}".strip()
