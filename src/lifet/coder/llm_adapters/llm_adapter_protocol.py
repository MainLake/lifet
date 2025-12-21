from abc import ABC, abstractmethod
from pydantic import BaseModel
from lifet.coder.llm_adapters.token_counter_protocol import TokenCounterProtocol

class CallToolLLM(BaseModel):
    tool_name: str
    arguments: dict

from typing import Optional

class RequestLLM(BaseModel):
    request_system_data: str
    request_user: str
    json_schema: dict
    agent_persona: Optional[str] = None
    katas_rules: Optional[str] = None

class ResponseLLM(BaseModel):
    reasoning: str
    response: str
    tool_calls: list[CallToolLLM]
    task_end: bool = False



class LLMAdapterProtocol(ABC):

    @property
    @abstractmethod
    def token_counter(self) -> TokenCounterProtocol:
        """The token counter for the adapter."""
        pass

    @abstractmethod
    def generate_content(self, request: RequestLLM) -> ResponseLLM:
        pass



