from lifet.tools.tool_prototipe import ToolPrototipe, ToolResponse
import os

class ReadFileTool(ToolPrototipe):
    """
    Tool for reading the content of a file.
    """

    def execute(self, **kwargs) -> ToolResponse:
        """
        Reads the content of a specified file.

        Parameters
        ----------
        file_path : str
            The path to the file to read.

        Returns
        -------
        ToolResponse
            A response containing:
                - result (str): The content of the file.
                - error (str | None): An error message if the file cannot be read.
        """
        file_path = kwargs.get("file_path")
        if not file_path:
            return ToolResponse(result="", error="No file_path provided")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return ToolResponse(result=content)
        except FileNotFoundError:
            return ToolResponse(result="", error=f"File not found: {file_path}")
        except Exception as e:
            return ToolResponse(result="", error=f"An error occurred: {e}")
