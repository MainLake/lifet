import unittest
from unittest.mock import MagicMock
from lifet.coder.coder import Coder
from lifet.memory.memory import InMemoryMemory
from lifet.coder.llm_adapters.llm_adapter_protocol import ResponseLLM, RequestLLM, CallToolLLM

class TestCoder(unittest.TestCase):

    def setUp(self):
        self.mock_llm_adapter = MagicMock()
        self.mock_memory = InMemoryMemory()
        self.coder = Coder(llm_adapter=self.mock_llm_adapter, memory=self.mock_memory)
        
        # Mock a tool
        self.mock_tool = MagicMock()
        self.mock_tool.execute.return_value.error = None
        self.mock_tool.execute.return_value.result = "Success"
        self.coder.tool_subscription([self.mock_tool])
        # Manually set the name, since __class__.__name__ is tricky with mocks
        self.coder.tools = {"MockTool": self.mock_tool}

if __name__ == '__main__':
    unittest.main()