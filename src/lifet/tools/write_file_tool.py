from lifet.tools.tool_prototipe import ToolPrototipe, ToolResponse
import os

class WriteFileTool(ToolPrototipe):
    """
    Tool for writing content to a file.
    """

    def execute(self, **kwargs) -> ToolResponse:
        """
        Writes content to a specified file.

        Parameters
        ----------
        file_path : str
            The path to the file to write to.
        content : str
            The content to write to the file.

        Returns
        -------
        ToolResponse
            A response containing:
                - result (str): A success message.
                - error (str | None): An error message if the file cannot be written.
        """
        file_path = kwargs.get("file_path")
        content = kwargs.get("content")

        if not file_path:
            return ToolResponse(result="", error="No file_path provided")
        
        if content is None:
            return ToolResponse(result="", error="No content provided")

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return ToolResponse(result=f"Successfully wrote to {file_path}")
        except Exception as e:
            return ToolResponse(result="", error=f"An error occurred: {e}")
