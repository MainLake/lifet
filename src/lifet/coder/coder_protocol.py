from abc import ABC, abstractmethod

from lifet.coder.llm_adapters.llm_adapter_protocol import RequestLLM, ResponseLLM, LLMAdapterProtocol
from lifet.tools.tool_prototipe import ToolPrototipe
from lifet.memory.memory_protocol import MemoryProtocol

class CoderProtocol(ABC):

    tools: list[ToolPrototipe] = []
    
    @abstractmethod
    def __init__(self, llm_adapter: LLMAdapterProtocol, memory: MemoryProtocol) -> None:
        self.llm_adapter = llm_adapter
        self.memory = memory

    @abstractmethod
    def code(self, request: RequestLLM) -> ResponseLLM | None:
        pass

    @abstractmethod
    def tool_subscription(self, tools: list[ToolPrototipe]) -> None:
        pass

