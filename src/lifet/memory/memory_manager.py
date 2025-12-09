class MemoryManager:

    def __init__(self, max_messages=10):
        self.max_messages = max_messages
        self.history = []

    def add(self, reasoning, response, tool_calls):
        entry = {
            "reasoning": reasoning,
            "response": response,
            "tool_calls": [
                {"tool": t.tool_name, "arguments": t.arguments}
                for t in tool_calls
            ]
        }
        self.history.append(entry)

        # Limitar tamaño para no crecer indefinidamente
        if len(self.history) > self.max_messages:
            self.history.pop(0)

    def build_context(self) -> str:
        """Convierte la memoria a un contexto compacto para el LLM."""
        if not self.history:
            return ""

        context = "\n### MEMORY CONTEXT START ###\n"

        for item in self.history:
            context += f"- Reasoning: {item['reasoning']}\n"
            context += f"- Response: {item['response']}\n"

            for t in item["tool_calls"]:
                context += f"- Tool call: {t['tool']} args={t['arguments']}\n"

            context += "---\n"

        context += "### MEMORY CONTEXT END ###\n"
        return context
