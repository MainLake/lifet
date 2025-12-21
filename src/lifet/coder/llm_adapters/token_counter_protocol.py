from abc import ABC, abstractmethod

class TokenCounterProtocol(ABC):
    """
    Protocol for token counting.
    """

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Counts the number of tokens in a given text.

        Parameters
        ----------
        text : str
            The text to count tokens from.

        Returns
        -------
        int
            The number of tokens in the text.
        """
        pass
