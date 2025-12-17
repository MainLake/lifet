from pydantic import BaseModel
from typing import Optional, Literal
from dotenv import load_dotenv
import os

from lifet.utils.objects import object_to_json

class LLMConfig(BaseModel):
    model_name: str
    service_name: Literal["gemini", "deepseek"]
    api_key: Optional[str] = None
    temperature: float = 0.7

    def __init__(self, **data):
        super().__init__(**data)
        load_dotenv()
        if not self.api_key:
            env_var_name = f"{self.service_name.upper()}_API_KEY"
            self.api_key = os.getenv(env_var_name)
        
        if not self.api_key:
            raise ValueError(
                f"API key not found. Please provide it directly, or set the {env_var_name} environment variable."
            )

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string",
            "description": "Tu proceso de pensamiento paso a paso"
        },
        "response": {
            "type": "string",
            "description": "Respuesta principal al usuario"
        },
        "tool_calls": {
            "type": "array",
            "description": "Lista de llamadas a herramientas/funciones",
            "items": {
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "Nombre exacto de la función"
                    },
                    "arguments": {
                        "type": "object",
                        "description": "Parámetros de la función",
                        "additionalProperties": True
                    }
                },
                "required": ["tool_name", "arguments"]
            }
        },
        "task_end": {
            "type": "boolean",
            "description": "Indica si la tarea ha terminado"
        }
    },
    "required": ["reasoning", "response", "tool_calls", "task_end"]
}

def get_response_schema_str() -> str | None:
    parse, error = object_to_json(RESPONSE_SCHEMA)
    if error:
        return None
    return parse

