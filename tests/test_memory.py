import unittest
from unittest.mock import MagicMock
from lifet.memory.memory import InMemoryMemory
from lifet.memory.summarizing_memory import SummarizingMemory
from lifet.memory.memory_protocol import MemoryInteraction
from lifet.coder.llm_adapters.llm_adapter_protocol import ResponseLLM, RequestLLM

class TestMemory(unittest.TestCase):

    def test_in_memory_memory(self):
        memory = InMemoryMemory(max_token_count=100)
        memory.save_memory(MemoryInteraction(role="user", content="This is a user message."))
        memory.save_memory(MemoryInteraction(role="assistant", content="This is an assistant response."))
        self.assertIn("[USER]\nThis is a user message.", memory.get_memory())
        self.assertIn("[ASSISTANT]\nThis is an assistant response.", memory.get_memory())

    def test_in_memory_memory_trimming(self):
        # With a small token count, the memory should be trimmed
        memory = InMemoryMemory(max_token_count=10) 
        memory.save_memory(MemoryInteraction(role="user", content="This is a long user message that should cause trimming."))
        memory.save_memory(MemoryInteraction(role="assistant", content="This is another long assistant response."))
        # The first message should be removed
        self.assertNotIn("user", memory.get_memory())

    def test_summarizing_memory(self):
        mock_adapter = MagicMock()
        mock_response = ResponseLLM(
            reasoning="",
            response="This is a summary.",
            tool_calls=[],
            task_end=True
        )
        mock_adapter.generate_content.return_value = mock_response

        memory = SummarizingMemory(llm_adapter=mock_adapter, max_buffer_size=2)
        memory.save_memory(MemoryInteraction(role="user", content="Message 1"))
        memory.save_memory(MemoryInteraction(role="assistant", content="Message 2"))
        memory.save_memory(MemoryInteraction(role="user", content="Message 3"))

        # The summarization should have been triggered
        self.assertIn("[SUMMARY]\nThis is a summary.", memory.get_memory())
        self.assertNotIn("Message 1", memory.get_memory())
        self.assertIn("Message 3", memory.get_memory())


if __name__ == '__main__':
    unittest.main()

