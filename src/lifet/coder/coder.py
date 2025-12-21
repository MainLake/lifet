from lifet.coder.coder_protocol import CoderProtocol
from lifet.coder.llm_adapters.llm_adapter_protocol import LLMAdapterProtocol, RequestLLM, ResponseLLM
from lifet.tools.tool_prototipe import ToolPrototipe
from lifet.memory.memory_protocol import MemoryProtocol, MemoryInteraction
from lifet.coder.llm_adapters.system_promt_llm import generate_system_prompt_llm
from lifet.utils.utils_so import get_info_so_json
import json

class Coder(CoderProtocol):
    """
    The Coder class orchestrates the interaction between the user, the LLM, and the tools.
    """
    tools: dict[str, ToolPrototipe] = {}

    def __init__(self, llm_adapter: LLMAdapterProtocol, memory: MemoryProtocol) -> None:
        self.llm_adapter = llm_adapter
        self.memory = memory

    def tool_subscription(self, tools: list[ToolPrototipe]) -> None:
        self.tools = {tool.__class__.__name__: tool for tool in tools}

    def get_tools_description(self) -> str:
        if not self.tools:
            return "No tools available."
        
        description = "Available tools:\n"
        for name, tool in self.tools.items():
            description += f"- {name}: {tool.__doc__}\n"
        return description

    def code(self, request: RequestLLM) -> ResponseLLM | None:
        self.memory.save_memory(MemoryInteraction(role="user", content=request.request_user))
        
        so_info = get_info_so_json()
        tools_description = self.get_tools_description()
        token_counter = self.llm_adapter.token_counter

        iteration_count = 0
        max_iterations = 10 

        while iteration_count < max_iterations:
            iteration_count += 1

            memory_context = self.memory.get_memory()
            
            current_system_prompt = generate_system_prompt_llm(
                so_info=so_info,
                tools_description=tools_description,
                history=memory_context,
                agent_persona=request.agent_persona,
                katas_rules=request.katas_rules
            )
            
            llm_request = RequestLLM(
                request_system_data=current_system_prompt,
                request_user=request.request_user,
                json_schema=request.json_schema,
                agent_persona=request.agent_persona,
                katas_rules=request.katas_rules
            )

            prompt_tokens = token_counter.count_tokens(current_system_prompt + request.request_user)

            responseLLM = self.llm_adapter.generate_content(llm_request)
            
            assistant_content = []
            if responseLLM.reasoning:
                assistant_content.append(f"Thought: {responseLLM.reasoning}")
            if responseLLM.tool_calls:
                tools_str = ", ".join([f"{tc.tool_name}({json.dumps(tc.arguments)})" for tc in responseLLM.tool_calls])
                assistant_content.append(f"Action: Call tool(s): {tools_str}")
            if responseLLM.response:
                assistant_content.append(f"Response: {responseLLM.response}")

            if assistant_content:
                self.memory.save_memory(MemoryInteraction(role="assistant", content=" ".join(assistant_content)))

            if responseLLM.task_end:
                return responseLLM
            
            if responseLLM.tool_calls:
                tool_results_content = []
                for tool_call in responseLLM.tool_calls:
                    if tool_call.tool_name in self.tools:
                        tool_to_execute = self.tools[tool_call.tool_name]
                        result = tool_to_execute.execute(**tool_call.arguments)

                        if result.error:
                            tool_results_content.append(f"Error from {tool_call.tool_name}: {result.error}")
                        else:
                            tool_results_content.append(f"Result of {tool_call.tool_name}: {result.result}")
                    else:

                        error_msg = f"Error: Tool '{tool_call.tool_name}' not found or not subscribed."
                        tool_results_content.append(error_msg)

                if tool_results_content:
                    self.memory.save_memory(MemoryInteraction(role="system", content=" ".join(tool_results_content)))
                            
        return None
