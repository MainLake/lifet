from lifet.coder.coder_protocol import CoderProtocol
from lifet.coder.llm_adapters.llm_adapter_protocol import LLMAdapterProtocol, RequestLLM, ResponseLLM
from lifet.tools.tool_prototipe import ToolPrototipe
from lifet.memory.memory_protocol import MemoryProtocol, MemoryInteraction
from lifet.coder.llm_adapters.system_promt_llm import generate_system_prompt_llm
from lifet.utils.utils_so import get_info_so_json
import json

class Coder(CoderProtocol):

    tools: list[ToolPrototipe] = []

    def __init__(self, llm_adapter: LLMAdapterProtocol, memory: MemoryProtocol) -> None:
        self.llm_adapter = llm_adapter
        self.memory = memory

    def tool_subscription(self, tools: list[ToolPrototipe]) -> None:
        self.tools = tools

    def get_tools_description(self) -> str:
        if not self.tools:
            return "No tools available."
        description = "Available tools:\n"
        for tool in self.tools:
            description += f"- {tool.__class__.__name__}: {tool.__doc__}\n"
        return description

    def code(self, request: RequestLLM) -> ResponseLLM | None:
        
        print("=== INICIANDO AGENTE CODER ===")
        print(f"Tools Loaded:")
        for t in self.tools:
            print(f"  └─ {t.__class__.__name__}")
        print("-" * 60)

        # Save user request to memory
        self.memory.save_memory(MemoryInteraction(role="user", content=request.request_user))
        
        # Store the initial static parts of the system prompt from the original request
        so_info = get_info_so_json() # Assuming this is static for the session
        tools_description = self.get_tools_description()

        end_task = False
        iteration_count = 1 

        while not end_task:
            
            print(f"\n>>> ITERACIÓN #{iteration_count}")

            # Get memory and generate the full system prompt for this iteration
            memory_context = self.memory.get_memory()
            
            current_system_prompt = generate_system_prompt_llm(
                response_schema=None, # Not used in the optimized prompt
                so_info=so_info,
                tools_description=tools_description,
                history=memory_context
            )
            
            # Create a new request for the LLM for this iteration
            llm_request = RequestLLM(
                request_system_data=current_system_prompt,
                request_user=request.request_user, # The original user request is passed for context
                json_schema=request.json_schema
            )

            # Llamada al LLM
            responseLLM = self.llm_adapter.generate_content(llm_request)
            print("ResponseLLM: ", responseLLM)
            
            # Save assistant response to memory in a compact format
            assistant_content = []
            if responseLLM.reasoning:
                assistant_content.append(f"Thought: {responseLLM.reasoning}")
            if responseLLM.tool_calls:
                tools_str = ", ".join([f"{tc.tool_name}({json.dumps(tc.arguments)})" for tc in responseLLM.tool_calls])
                assistant_content.append(f"Action: Call tool(s): {tools_str}")
            if responseLLM.response:
                assistant_content.append(f"Response: {responseLLM.response}")

            if assistant_content:
                self.memory.save_memory(MemoryInteraction(role="assistant", content="\n".join(assistant_content)))

            if responseLLM.reasoning:
                print(f"🧠 Reasoning: {responseLLM.reasoning}")
            
            if responseLLM.response:
                print(f"🗣️  Response: {responseLLM.response}")

            end_task = responseLLM.task_end

            if end_task:
                print("\n=== TAREA FINALIZADA ===")
                return responseLLM
            
            if responseLLM.tool_calls:
                print(f"\n🛠️  TOOL CALLS DETECTED ({len(responseLLM.tool_calls)})")
                
                tool_results_content = []
                for tool in responseLLM.tool_calls:
                    tool_found = False
                    for tool_available in self.tools:
                        if tool_available.__class__.__name__ == tool.tool_name:
                            tool_found = True
                            print(f"   ⚡ Executing: {tool.tool_name}")
                            print(f"      Args: {tool.arguments}")
                            
                            result = tool_available.execute(**tool.arguments)

                            if result.error:
                                print(f"      ❌ Error: {result.error}")
                                tool_results_content.append(f"Error from {tool.tool_name}: {result.error}")
                            else:
                                output_display = str(result.result)
                                if len(output_display) > 200:
                                    output_display = output_display[:200] + "... [truncated]"
                                
                                print(f"      ✅ Result: {output_display}")
                                tool_results_content.append(f"Result of {tool.tool_name}: {result.result}")
                            break 
                    if not tool_found:
                        error_msg = f"Error: Tool '{tool.tool_name}' not found or not subscribed."
                        print(f"      ❌ {error_msg}")
                        tool_results_content.append(error_msg)

                if tool_results_content:
                    self.memory.save_memory(MemoryInteraction(role="system", content="\n".join(tool_results_content)))
                            
            iteration_count += 1
            print(f"{'-'*40}")

        print('\n\n')
        return None
