from lifet.tools.tool_prototipe import ToolPrototipe, ToolResponse
import os

class ListFilesTool(ToolPrototipe):
    """
    Tool for listing files in a directory.
    """

    def execute(self, **kwargs) -> ToolResponse:
        """
        Lists files and directories at a given path.

        Parameters
        ----------
        path : str, optional
            The path to the directory to list. Defaults to the current directory.

        Returns
        -------
        ToolResponse
            A response containing:
                - result (str): A newline-separated list of files and directories.
                - error (str | None): An error message if the path is invalid.
        """
        path = kwargs.get("path", ".")

        try:
            if not os.path.isdir(path):
                return ToolResponse(result="", error=f"Path is not a valid directory: {path}")
                
            files = os.listdir(path)
            return ToolResponse(result="\n".join(files))
        except Exception as e:
            return ToolResponse(result="", error=f"An error occurred: {e}")
