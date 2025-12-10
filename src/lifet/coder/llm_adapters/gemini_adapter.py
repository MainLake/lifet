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
            #parser_text_to_dict = self.parse_dict(request_llm.text)
            response = request_llm.text
            a = self.find_chunck("--TOOLNAME--", "--ENDTOOLNAME--", response, False)
            b = self.find_chunck("--COMMAND--", "--ENDCOMMAND--", response, False)

            parser_text_to_dict = {
                "reasoning": self.find_chunck("--REASONING--", "--ENDREASONING--", response), 
                "response": self.find_chunck("--RESPONSE--", "--ENDRESPONSE--", response),
                "tool_calls": [
                    {
                        "tool_name": k, 
                        "arguments": {
                            "command": v
                        }
                    } for k, v in zip(a, b)
                ]
            }
            
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
    
    def find_chunck(
        self, 
        text_start: str, 
        text_end: str, 
        text: str, 
        first_only: bool = True
    ) -> str:
        lines = []
        found = False
        
        for line in text.splitlines():
            cleaned_line = line.strip()
        
            if cleaned_line == "":
                continue
            
            if cleaned_line.startswith(text_start):
                found = True
                continue
                
            if found:
                if cleaned_line.startswith(text_end):
                    found = False
                    
                    if first_only: 
                        break
                
                else:
                    lines.append(cleaned_line)

        return "".join(lines) if first_only else lines
