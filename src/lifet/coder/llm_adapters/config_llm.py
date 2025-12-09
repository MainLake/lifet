from pydantic import BaseModel

from lifet.utils.objects import object_to_json

class LLMConfig(BaseModel):
    model_name: str
    api_key: str
    temperature: float = 0.7


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

