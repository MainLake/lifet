import unittest
from unittest.mock import patch, MagicMock
from lifet.coder.llm_adapters.gemini_token_counter import GeminiTokenCounter
from lifet.coder.llm_adapters.deepseek_token_counter import DeepSeekTokenCounter

class TestTokenCounters(unittest.TestCase):

    @patch('google.generativeai.GenerativeModel')
    def test_gemini_token_counter(self, mock_generative_model):
        mock_model_instance = MagicMock()
        mock_model_instance.count_tokens.return_value = MagicMock(total_tokens=10)
        mock_generative_model.return_value = mock_model_instance
        
        # We need to patch configure as well, so it doesn't try to use a real key
        with patch('google.generativeai.configure'):
            counter = GeminiTokenCounter(model_name="gemini-pro", api_key="fake_key")
            token_count = counter.count_tokens("Hello, world!")
            self.assertEqual(token_count, 10)

    def test_deepseek_token_counter(self):
        counter = DeepSeekTokenCounter()
        # "Hello, world!" is 13 characters. 13 // 4 = 3
        token_count = counter.count_tokens("Hello, world!")
        self.assertEqual(token_count, 3)
        
        # Test with an empty string
        token_count_empty = counter.count_tokens("")
        self.assertEqual(token_count_empty, 0)

if __name__ == '__main__':
    unittest.main()
