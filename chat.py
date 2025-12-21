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

console = Console()

def initialize_coder():
    """Initializes and configures the Coder agent and its components."""
    
    if not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        console.print("\n[bold red]ERROR: API Key not found.[/bold red]")
        console.print("Please create a .env file and set DEEPSEEK_API_KEY or GEMINI_API_KEY.")
        return None

    try:
        config = LLMConfig(model_name="deepseek-chat", service_name="deepseek")
        token_counter = DeepSeekTokenCounter()
        adapter = DeepSeekAdapter(config_llm=config, token_counter=token_counter)
        
        # config = LLMConfig(model_name="gemini-1.5-flash", service_name="gemini")
        # token_counter = GeminiTokenCounter(model_name=config.model_name, api_key=config.api_key)
        # adapter = GeminiAdapter(config_llm=config, token_counter=token_counter)

    except ValueError as e:
        console.print(f"\n[bold red]Configuration Error: {e}[/bold red]")
        return None

    coder = Coder(llm_adapter=adapter, memory=InMemoryMemory())
    coder.tool_subscription([ShellTool(), ReadFileTool(), WriteFileTool(), ListFilesTool()])
    
    console.print("[yellow]Agent initialized successfully.[/yellow]")
    console.print("[yellow]Available commands: /reset, /exit, /quit[/yellow]")
    console.print("-" * 40)
    
    return coder

def display_agent_thought(response: ResponseLLM):
    """Displays the agent's reasoning and tool calls in a panel."""
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

    coder = initialize_coder()
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

            # This part is moved from the Coder to the CLI
            # We can inspect the number of tokens before making the call
            # This is a simplified version; a more accurate count would require
            # getting the fully rendered prompt from the coder.
            token_count = coder.llm_adapter.token_counter.count_tokens(user_input)
            console.print(f"[dim]Approx. prompt tokens: {token_count}[/dim]")

            final_response = coder.code(task)
            
            if final_response:
                display_agent_thought(final_response)
                if final_response.response:
                    console.print(f"\n[blue]Agent:[/blue] {final_response.response}")
                else:
                    console.print("\n[yellow]Agent: Task finished, but no final response was provided.[/yellow]")
            else:
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
