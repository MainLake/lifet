from abc import ABC, abstractmethod
from lifet.tools.tool_prototipe import ToolResponse


class CoderCallbackHandler(ABC):
    """
    Abstract base class for callback handlers that can be used to monitor
    the execution of the Coder.
    """

    def on_tool_start(self, tool_name: str, args: dict) -> None:
        """Called when a tool is about to be executed."""
        pass

    def on_tool_end(self, tool_name: str, response: ToolResponse) -> None:
        """Called after a tool has been executed."""
        pass
