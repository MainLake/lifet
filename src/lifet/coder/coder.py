from typing import List, Optional
import json
import re
from lifet.coder.coder_protocol import CoderProtocol
from lifet.coder.llm_adapters.llm_adapter_protocol import LLMAdapterProtocol, RequestLLM, ResponseLLM
from lifet.tools.tool_prototipe import ToolPrototipe, ToolResponse
from lifet.memory.memory_protocol import MemoryProtocol, MemoryInteraction
from lifet.memory.layered_memory import LayeredMemory
from lifet.coder.llm_adapters.system_promt_llm import generate_system_prompt_llm
from lifet.utils.utils_so import get_info_so_json
from lifet.coder.coder_callbacks import CoderCallbackHandler

def extract_json_from_text(text: str) -> dict:
    """Attempts to extract JSON from text that might contain markdown or comments."""
    # Look for JSON code blocks
    json_pattern = r'```json\s*(.*?)\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    
    # Look for raw JSON object
    json_pattern = r'\{.*\}'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    
    raise ValueError("Could not extract valid JSON from text")

class Coder(CoderProtocol):
    """
    The Coder class orchestrates the interaction between the user, the LLM, and the tools.
    """
    tools: dict[str, ToolPrototipe] = {}

    def __init__(
        self, 
        llm_adapter: LLMAdapterProtocol, 
        memory: Optional[MemoryProtocol] = None,
        callbacks: Optional[List[CoderCallbackHandler]] = None
    ) -> None:
        self.llm_adapter = llm_adapter
        self.memory = memory if memory else LayeredMemory()
        self.callbacks = callbacks or []

    def tool_subscription(self, tools: list[ToolPrototipe]) -> None:
        self.tools = {tool.__class__.__name__: tool for tool in tools}

    def get_tools_description(self) -> str:
        if not self.tools:
            return "No tools available."
        
        description = "Available tools:\n"
        for name, tool in self.tools.items():
            description += f"- {name}: {tool.__doc__}\n"
        return description

    def _notify_tool_start(self, tool_name: str, args: dict):
        for handler in self.callbacks:
            handler.on_tool_start(tool_name, args)

    def _notify_tool_end(self, tool_name: str, response: ToolResponse):
        for handler in self.callbacks:
            handler.on_tool_end(tool_name, response)

    def code(self, request: RequestLLM) -> ResponseLLM | None:
        self.memory.save_memory(MemoryInteraction(role="user", content=request.request_user))
        
        so_info = get_info_so_json()
        tools_description = self.get_tools_description()

        iteration_count = 0
        max_iterations = 20
        MAX_RETRIES = 3
        
        current_user_request = request.request_user

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
            
            # Additional prompt reinforcement for JSON
            full_user_prompt = f"{current_user_request}\n\nIMPORTANT: Respond with VALID JSON ONLY."

            llm_request = RequestLLM(
                request_system_data=current_system_prompt,
                request_user=full_user_prompt,
                json_schema=request.json_schema,
                agent_persona=request.agent_persona,
                katas_rules=request.katas_rules
            )
            
            # After the first iteration, the user request is considered processed
            current_user_request = ""

            responseLLM = None
            retry_count = 0
            
            while retry_count < MAX_RETRIES:
                try:
                    raw_response = self.llm_adapter.generate_content(llm_request)
                    
                    if raw_response is None:
                        raise ValueError("Received an empty response from the language model.")
                    
                    responseLLM = raw_response
                    break 
                    
                except Exception as e:
                    retry_count += 1
                    error_msg = f"Error during LLM call (Attempt {retry_count}/{MAX_RETRIES}): {e}"
                    # print(f"⚠️ {error_msg}")
                    
                    if retry_count >= MAX_RETRIES:
                        self.memory.save_memory(MemoryInteraction(role="system", content=f"{error_msg}. Failed to get valid JSON."))
                        break
            
            if not responseLLM:
                continue

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
                MAX_TOOL_OUTPUT_LENGTH = 1000
                for tool_call in responseLLM.tool_calls:
                    if tool_call.tool_name in self.tools:
                        tool_to_execute = self.tools[tool_call.tool_name]
                        
                        self._notify_tool_start(tool_call.tool_name, tool_call.arguments)

                        try:
                            result = tool_to_execute.execute(**tool_call.arguments)
                            self._notify_tool_end(tool_call.tool_name, result)
                            
                            if result.error:
                                tool_results_content.append(f"Error from {tool_call.tool_name}: {result.error}")
                            else:
                                truncated_result = result.result
                                if len(truncated_result) > MAX_TOOL_OUTPUT_LENGTH:
                                    truncated_result = truncated_result[:MAX_TOOL_OUTPUT_LENGTH] + " (truncated)"
                                tool_results_content.append(f"Result of {tool_call.tool_name}: {truncated_result}")
                        except Exception as e:
                            error_msg = f"Fatal error executing tool {tool_call.tool_name}: {e}"
                            tool_results_content.append(error_msg)
                            error_response = ToolResponse(result="", error=error_msg)
                            self._notify_tool_end(tool_call.tool_name, error_response)
                    else:
                        error_msg = f"Error: Tool '{tool_call.tool_name}' not found or not subscribed."
                        tool_results_content.append(error_msg)

                if tool_results_content:
                    self.memory.save_memory(MemoryInteraction(role="tool", content=" ".join(tool_results_content)))
                            
        failure_reason = f"Task failed: Maximum number of iterations ({max_iterations}) reached."
        return ResponseLLM(
            reasoning=failure_reason,
            response="I was unable to complete the task after multiple attempts. Please try rephrasing the request or check the tool results for errors.",
            tool_calls=[],
            task_end=True
        )
