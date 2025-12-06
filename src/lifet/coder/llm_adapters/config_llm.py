from pydantic import BaseModel

class LLMConfig(BaseModel):
    model_name: str
    api_key: str
    temperature: float = 0.7
