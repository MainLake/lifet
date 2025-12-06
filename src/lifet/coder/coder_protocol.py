from abc import ABC, abstractmethod

from lifet.coder.llm_adapters.llm_adapter_protocol import RequestLLM, ResponseLLM
from lifet.coder.llm_adapters.llm_adapter_protocol import LLMAdapterProtocol
from lifet.tools.tool_prototipe import ToolPrototipe

class CoderProtocol(ABC):

    tools: list[ToolPrototipe] = []
    
    @abstractmethod
    def __init__(self, llm_adapter: LLMAdapterProtocol) -> None:
        self.llm_adapter = llm_adapter

    @abstractmethod
    def code(self, request: RequestLLM) -> ResponseLLM | None:
        pass

    @abstractmethod
    def tool_subscription(self, tools: list[ToolPrototipe]) -> None:
        pass

