from abc import ABC, abstractmethod
from pydantic import BaseModel

class CallToolLLM(BaseModel):
    tool_name: str
    arguments: dict

class RequestLLM(BaseModel):
    request_system_data: str
    request_user: str
    json_schema: dict

class ResponseLLM(BaseModel):
    reasoning: str
    response: str
    tool_calls: list[CallToolLLM]
    task_end: bool = False



class LLMAdapterProtocol(ABC):

    @abstractmethod
    def generate_content(self, request: RequestLLM) -> ResponseLLM:
        pass



