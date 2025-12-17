import os
from lifet.coder.coder import Coder
from lifet.coder.llm_adapters.deepseek_adapter import DeepSeekAdapter
from lifet.coder.llm_adapters.config_llm import LLMConfig
from lifet.tools.shell_tool import ShellTool
from lifet.coder.llm_adapters.llm_adapter_protocol import RequestLLM
from lifet.memory.memory import InMemoryMemory
from dotenv import load_dotenv

def main():
    """
    Función principal para ejecutar el chat interactivo con el agente Coder.
    """
    load_dotenv()
    print("Welcome to the lifet interactive chat!")
    print("Type 'exit' or 'quit' to end the session.")
    print("-" * 40)

    # 1. Check for API Key
    if not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("\nERROR: API Key not found.")
        print("Please create a .env file and set DEEPSEEK_API_KEY or GEMINI_API_KEY.")
        print("See .env.example for more details.")
        return

    # 2. Configure the LLM
    # This example uses DeepSeek. Change 'service_name' to 'gemini' to use Gemini.
    try:
        config = LLMConfig(
            model_name="deepseek-chat",
            service_name="deepseek"
        )
    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        return

    # 3. Instantiate the core components
    adapter = DeepSeekAdapter(config_llm=config) # A new memory for each session
    coder = Coder(llm_adapter=adapter, memory=InMemoryMemory())

    # 4. Subscribe tools
    coder.tool_subscription([ShellTool()])

    # 5. Start interactive loop
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Ending chat session. Goodbye!")
                break

            # Create the task request for the Coder
            task = RequestLLM(
                request_system_data="", # Managed internally by the Coder
                request_user=user_input,
                json_schema={}
            )

            # Execute the Coder
            final_response = coder.code(task)

            # Print the final response to the user
            if final_response and final_response.response:
                print(f"\nAgent: {final_response.response}")
            else:
                print("\nAgent: Task finished, but no final response was provided.")
        
        except (KeyboardInterrupt, EOFError):
            print("\n\nEnding chat session. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            print("Restarting the session memory.")
            # Reset memory on error to start fresh
            coder = Coder(llm_adapter=adapter, memory=InMemoryMemory())
            coder.tool_subscription([ShellTool()])


if __name__ == "__main__":
    main()
