from lifet.coder.llm_adapters.token_counter_protocol import TokenCounterProtocol

class DeepSeekTokenCounter(TokenCounterProtocol):
    """
    A simple token counter for DeepSeek models that estimates token count
    based on character count.
    """
    def count_tokens(self, text: str) -> int:
        """
        Estimates the number of tokens in a given text.
        This implementation uses a rough estimation of 4 characters per token.

        Parameters
        ----------
        text : str
            The text to count tokens from.

        Returns
        -------
        int
            The estimated number of tokens in the text.
        """
        return len(text) // 4
