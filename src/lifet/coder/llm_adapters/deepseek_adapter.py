import json
from lifet.coder.llm_adapters.config_llm import LLMConfig
from lifet.coder.llm_adapters.llm_adapter_protocol import LLMAdapterProtocol, RequestLLM, ResponseLLM, CallToolLLM
from lifet.coder.llm_adapters.response_cleaner import ResponseCleanerProtocol, GeminiJSONCleaner
from openai import OpenAI

class DeepSeekAdapter(LLMAdapterProtocol):

    def __init__(self, config_llm: LLMConfig, response_cleaner: ResponseCleanerProtocol = None) -> None:
        super().__init__()
        self.config_llm = config_llm
        self.client = OpenAI(api_key=self.config_llm.api_key, base_url="https://api.deepseek.com")
        self.response_cleaner = response_cleaner or GeminiJSONCleaner()

    def generate_content(self, request: RequestLLM) -> ResponseLLM:
        response_llm = self.client.chat.completions.create(
            model=self.config_llm.model_name,
            messages=[
                {
                    "role": "system",
                    "content": request.request_system_data
                },
                {
                    "role": "user",
                    "content": request.request_user
                }
            ],
            stream=False,
        )

        if not response_llm.choices[0].message.content:
            raise Exception("Error al generar el contenido")

        cleaned_response = self.response_cleaner.clean(response_llm.choices[0].message.content)
        parse_response_dict: dict = json.loads(cleaned_response)

        response_llm_object = ResponseLLM(
            reasoning=parse_response_dict.get("reasoning", ""),
            response=parse_response_dict.get("response", ""),
            task_end=parse_response_dict.get("task_end", False),
            tool_calls=[
                CallToolLLM(
                    tool_name=tool_call.get("tool_name", ""),
                    arguments=tool_call.get("arguments", {})
                )
                for tool_call in parse_response_dict.get("tool_calls", [])
            ]
        )

        return response_llm_object
