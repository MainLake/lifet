from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class ToolResponse(BaseModel):
    result: str
    error: str | None = None


class ToolPrototipe(ABC):

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResponse:
        pass
