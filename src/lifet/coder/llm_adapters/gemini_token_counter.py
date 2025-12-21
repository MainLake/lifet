from lifet.coder.llm_adapters.token_counter_protocol import TokenCounterProtocol
import google.generativeai as genai

class GeminiTokenCounter(TokenCounterProtocol):
    """
    Token counter for Gemini models.
    """
    def __init__(self, model_name: str, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def count_tokens(self, text: str) -> int:
        """
        Counts the number of tokens in a given text using the Gemini API.

        Parameters
        ----------
        text : str
            The text to count tokens from.

        Returns
        -------
        int
            The number of tokens in the text.
        """
        try:
            response = self.model.count_tokens(text)
            return response.total_tokens
        except Exception as e:
            print(f"Error counting tokens: {e}")
            # Fallback to a rough estimation
            return len(text) // 4
