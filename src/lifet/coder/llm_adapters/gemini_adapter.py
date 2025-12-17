from lifet.coder.llm_adapters.config_llm import LLMConfig
from lifet.coder.llm_adapters.llm_adapter_protocol import CallToolLLM, LLMAdapterProtocol, RequestLLM, ResponseLLM
from lifet.coder.llm_adapters.response_cleaner import ResponseCleanerProtocol, GeminiJSONCleaner
from google import genai
import json

class GeminiAdapter(LLMAdapterProtocol):

    def __init__(self, config_llm: LLMConfig, response_cleaner: ResponseCleanerProtocol = None) -> None:
        super().__init__()
        self.config_llm = config_llm
        self.client = genai.Client(api_key=self.config_llm.api_key)
        self.response_cleaner = response_cleaner or GeminiJSONCleaner()

    def generate_content(self, request: RequestLLM) -> ResponseLLM:

        parse_str_request = f"System: {request.request_system_data}\nUser: {request.request_user}"

        request_llm = self.client.models.generate_content(
            model=self.config_llm.model_name,
            contents=parse_str_request,
        )

        if not request_llm.text:
            raise ValueError("No response from Gemini API")

        try:
            cleaned_response = self.response_cleaner.clean(request_llm.text)
            parser_text_to_dict = json.loads(cleaned_response)

            new_response_llm = ResponseLLM(
                reasoning=parser_text_to_dict.get("reasoning", ""),
                response=parser_text_to_dict.get("response", ""),
                task_end=parser_text_to_dict.get("task_end", False),
                tool_calls=[
                    CallToolLLM(
                        tool_name=tool_call.get("tool_name", ""),
                        arguments=tool_call.get("arguments", {})
                    )
                    for tool_call in parser_text_to_dict.get("tool_calls", [])
                ]
            )

            return new_response_llm

        except json.JSONDecodeError as e:
            print("Response text:", request_llm.text)
            raise ValueError(f"Failed to parse response: {e}")
