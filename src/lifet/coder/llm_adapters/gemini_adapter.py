from lifet.coder.llm_adapters.config_llm import LLMConfig
from lifet.coder.llm_adapters.llm_adapter_protocol import CallToolLLM, LLMAdapterProtocol
from lifet.coder.llm_adapters.llm_adapter_protocol import RequestLLM, ResponseLLM
from google import genai
import json
import re
import xml.etree.ElementTree as ET


class GeminiAdapter(LLMAdapterProtocol):

    def __init__(self, config_llm: LLMConfig) -> None:
        super().__init__()
        self.config_llm = config_llm
        self.client = genai.Client(api_key=self.config_llm.api_key)

    def generate_content(self, request: RequestLLM) -> ResponseLLM:

        parse_str_request = f"System: {request.request_system_data}\nUser: {request.request_user}"

        request_llm = self.client.models.generate_content(
            model=self.config_llm.model_name,
            contents=parse_str_request,
        )

        if not request_llm.text:
            raise ValueError("No response from Gemini API")

        try:
            #parser_text_to_dict = json.loads(self.clean_response(request_llm.text))
            parser_text_to_dict = self.parse_dict(request_llm.text)

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
    
    def parse_dict(self, xml_text: str) -> dict:
        print(xml_text)
        tree = ET.fromstring(xml_text)

        reasoning = tree.find('reasoning').text.strip()
        response = tree.find('response').text.strip()

        task_end_str = tree.find('task_end').text.strip().lower()
        task_end = True if task_end_str == 'true' else False

        tools = []
        
        for tool in tree.findall('tool_calls/tool'):
            tname = tool.find('tool_name').text.strip()
            command_text = tool.find('arguments/command').text.strip()
            tools.append({
                "tool_name": tname,
                "arguments": {
                    "command": command_text
                }
            })

        return {
            "reasoning": reasoning,
            "response": response,
            "tool_calls": tools,
            "task_end": task_end
        }
