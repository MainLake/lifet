import json
from lifet.coder.llm_adapters.config_llm import LLMConfig
from lifet.coder.llm_adapters.llm_adapter_protocol import LLMAdapterProtocol
from lifet.coder.llm_adapters.llm_adapter_protocol import RequestLLM, ResponseLLM
from lifet.coder.llm_adapters.llm_adapter_protocol import CallToolLLM
from openai import OpenAI
import re

class DeepSeekAdapter(LLMAdapterProtocol):

    def __init__(self, config_llm: LLMConfig) -> None:
        super().__init__()
        self.config_llm = config_llm
        self.client = OpenAI(api_key=self.config_llm.api_key, base_url="https://api.deepseek.com")

    def generate_content(self, request: RequestLLM) -> ResponseLLM:
        response_llm = self.client.chat.completions.create(
            model=self.config_llm.model_name,
            messages=[
                {
                    "role": "system",
                    "content": request.request_system_data
                },
                # Implementacion de la memoria
                {
                    "role": "system",
                    "content": ""
                },
                # Solicitud a realizar
                {
                    "role": "user",
                    "content": request.request_user
                }
            ],
            stream=False,
        )

        if not response_llm.choices[0].message.content:
            raise Exception("Error al generar el contenido")

        parse_response_dict: dict = json.loads(self.clean_response(response_llm.choices[0].message.content))

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

    def clean_response(self, response: str) -> str:
            clean_text = response.strip()

            # 1. Eliminar bloques Markdown
            match = re.search(r"```(?:json)?\s*(.*)\s*```", clean_text, re.DOTALL)
            if match:
                clean_text = match.group(1)
            
            clean_text = clean_text.strip()

            # 2. FIX 1: Convertir \' a ' 
            # (JSON prohíbe escapar comillas simples, Python lo ama)
            clean_text = clean_text.replace(r"\'", "'")

            # 3. FIX 2 (NUEVO): Convertir \\" a \"
            # El error actual: El LLM envió \\" (Backslash + Fin de string).
            # Lo corregimos a \" (Comilla escapada dentro del string).
            clean_text = clean_text.replace(r'\\"', r'\"')

            # 4. FIX 3 (OPCIONAL PERO RECOMENDADO): Saltos de línea literales
            # A veces el LLM da "Enter" dentro del string JSON en lugar de poner \n
            # Esto elimina saltos de línea reales dentro del JSON para evitar otro error común.
            # clean_text = clean_text.replace("\n", "\\n") 
            # (Nota: Usa el FIX 3 con cuidado, a veces rompe el formato bonito si no es dentro de strings)

            return clean_text
