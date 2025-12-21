import os
import json
from dotenv import load_dotenv
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.panel import Panel

from lifet.coder.coder import Coder
from lifet.coder.llm_adapters.config_llm import LLMConfig
from lifet.coder.llm_adapters.deepseek_adapter import DeepSeekAdapter
from lifet.coder.llm_adapters.deepseek_token_counter import DeepSeekTokenCounter
from lifet.coder.llm_adapters.gemini_adapter import GeminiAdapter
from lifet.coder.llm_adapters.gemini_token_counter import GeminiTokenCounter
from lifet.coder.llm_adapters.llm_adapter_protocol import RequestLLM, ResponseLLM
from lifet.memory.memory import InMemoryMemory
from lifet.tools.shell_tool import ShellTool
from lifet.tools.read_file_tool import ReadFileTool
from lifet.tools.write_file_tool import WriteFileTool
from lifet.tools.list_files_tool import ListFilesTool

from lifet.coder.coder_callbacks import CoderCallbackHandler
from lifet.tools.tool_prototipe import ToolResponse

console = Console()

class RichCallbackHandler(CoderCallbackHandler):
    """A callback handler that prints tool execution status using rich."""
    def on_tool_start(self, tool_name: str, args: dict) -> None:
        console.print(f"Executing tool [bold magenta]{tool_name}[/bold magenta] with args: {args}")

    def on_tool_end(self, tool_name: str, response: ToolResponse) -> None:
        if response.error:
            console.print(f"Tool [bold magenta]{tool_name}[/bold magenta] finished with an [bold red]error[/bold red]: {response.error}")
        else:
            # Truncate long results for display
            result_display = response.result
            if len(result_display) > 200:
                result_display = result_display[:200] + "..."
            console.print(f"Tool [bold magenta]{tool_name}[/bold magenta] finished successfully. Result: [dim]{result_display}[/dim]")


def initialize_coder(verbose: bool = True):
    """Initializes and configures the Coder agent and its components."""
    
    if not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        console.print("\n[bold red]ERROR: API Key not found.[/bold red]")
        console.print("Please create a .env file and set DEEPSEEK_API_KEY or GEMINI_API_KEY.")
        return None

    try:
        # Switch between models by commenting/uncommenting
        config = LLMConfig(model_name="deepseek-chat", service_name="deepseek")
        token_counter = DeepSeekTokenCounter()
        adapter = DeepSeekAdapter(config_llm=config, token_counter=token_counter)
        
        # config = LLMConfig(model_name="gemini-1.5-flash", service_name="gemini")
        # token_counter = GeminiTokenCounter(model_name=config.model_name, api_key=config.api_key)
        # adapter = GeminiAdapter(config_llm=config, token_counter=token_counter)

    except ValueError as e:
        console.print(f"\n[bold red]Configuration Error: {e}[/bold red]")
        return None

    callbacks = [RichCallbackHandler()] if verbose else []
    coder = Coder(llm_adapter=adapter, memory=InMemoryMemory(), callbacks=callbacks)
    coder.tool_subscription([ShellTool()])
    
    console.print("[yellow]Agent initialized successfully.[/yellow]")
    console.print("[yellow]Available commands: /reset, /exit, /quit[/yellow]")
    console.print("-" * 40)
    
    return coder

def display_agent_thought(response: ResponseLLM):
    """Displays the agent's reasoning and tool calls in a panel."""
    if not response:
        return
    if not response.reasoning and not response.tool_calls:
        return
        
    output = ""
    if response.reasoning:
        output += f"[bold]Reasoning:[/bold]\n{response.reasoning}\n\n"
    
    if response.tool_calls:
        output += "[bold]Tool Calls:[/bold]\n"
        for tool_call in response.tool_calls:
            args = json.dumps(tool_call.arguments)
            output += f"- {tool_call.tool_name}({args})\n"
            
    console.print(Panel(output, title="Agent's Thought Process", border_style="dim blue"))


def main():
    """
    Main function to run the interactive chat with the Coder agent.
    """
    load_dotenv()
    console.print("[bold green]Welcome to the lifet interactive chat![/bold green]")

    # Verbose mode is on by default for the interactive chat
    coder = initialize_coder(verbose=True)
    if not coder:
        return

    history = InMemoryHistory()
    path_completer = PathCompleter()

    while True:
        try:
            user_input = prompt("You: ", history=history, completer=path_completer, bottom_toolbar="Use Tab for file completion")

            if user_input.lower() in ["/exit", "/quit"]:
                console.print("[yellow]Ending chat session. Goodbye![/yellow]")
                break
            
            if user_input.lower() == "/reset":
                console.print("\n[yellow]Resetting agent memory...[/yellow]")
                coder.memory = InMemoryMemory()
                console.print("[yellow]Memory has been reset.[/yellow]")
                continue

            task = RequestLLM(
                request_system_data="",
                request_user=user_input,
                json_schema={}
            )
            
            final_response = coder.code(task)
            
            display_agent_thought(final_response)

            if final_response and final_response.response:
                console.print(f"\n[blue]Agent:[/blue] {final_response.response}")
            else:
                # This case is hit if the agent self-correction loop fails
                console.print("\n[bold red]Agent could not complete the task after several attempts.[/bold red]")

        except (KeyboardInterrupt, EOFError):
            console.print("\n\n[yellow]Ending chat session. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]An unexpected error occurred in the chat loop: {e}[/bold red]")
            # Continue the loop to allow the user to try again.
            continue
if __name__ == "__main__":
    main()
