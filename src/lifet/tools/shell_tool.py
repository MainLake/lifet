
from lifet.tools.tool_prototipe import ToolPrototipe
from lifet.tools.tool_prototipe import ToolResponse

from lifet.tools.tool_prototipe import ToolPrototipe
from lifet.tools.tool_prototipe import ToolResponse
import subprocess


class ShellTool(ToolPrototipe):
    """
    Tool that executes shell commands on the local system.
    """

    def execute(self, **kwargs) -> ToolResponse:
        """
        Execute a shell command provided in the arguments dictionary.

        Parameters
        ----------
        arguments : dict
            A dictionary containing the command to execute. 
            Expected key:
                - "command" (str): The shell command to run.

        Returns
        -------
        ToolResponse
            A response containing:
                - result (str): The stdout output from the command.
                - error (str | None): Any stderr output if the command fails.

        Notes
        -----
        This method uses `subprocess.run` with `shell=True`. 
        Be careful when executing commands built from untrusted user input.
        """

        command = kwargs.get("command")
        if not command:
            return ToolResponse(result="", error="No command provided")

        try:
            completed_process = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return ToolResponse(result=completed_process.stdout)
        except subprocess.CalledProcessError as e:
            return ToolResponse(result="", error=e.stderr)

