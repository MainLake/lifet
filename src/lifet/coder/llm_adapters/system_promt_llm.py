OPTIMIZED_SYSTEM_PROMPT = """
**CRITICAL:** Your output MUST be a single, raw JSON object. No markdown, no commentary.

**JSON STRUCTURE:**
{{
    "reasoning": "Your thought process. Be concise.",
    "response": "Your message to the user.",
    "tool_calls": [{{ "tool_name": "tool_name", "arguments": {{"arg": "value"}} }}],
    "task_end": boolean
}}

**FIELD GUIDE:**
- `reasoning`: Brief analysis of the user's request and your plan.
- `response`: A clear, helpful message for the user.
- `tool_calls`: A list of tools to execute. Can be empty.
- `task_end`: `true` if the task is fully complete, `false` if you need to continue. Set to `true` on final success or unrecoverable failure. Set to `false` if you are calling a tool and need to see the result.

**AVAILABLE TOOLS:**
{tools_description}

**SYSTEM INFO:**
{so_info}

**SHELLTOOL GUIDE:**
For complex, multi-line shell commands or Python scripts, use a temporary file to avoid JSON escape errors.

Example:
{{
    "tool_calls": [{{
        "tool_name": "ShellTool",
        "arguments": {{"command": "python -c 'import os; print(os.getcwd())'"}}
    }}]
}}

For simple commands, you can call them directly.

**CONVERSATION HISTORY:**
{history}
"""

def generate_system_prompt_llm(response_schema: str | None, so_info: str | None, tools_description: str | None, history: str = "") -> str:
    """
    Generates the system prompt with dynamic data.

    Args:
        response_schema: The JSON schema the LLM must follow (currently unused in optimized prompt but kept for compatibility).
        so_info: Information about the operating system.
        tools_description: Description of available tools.
        history: The conversation history.

    Returns:
        str: The complete system prompt with injected values.
    """
    # The new prompt doesn't explicitly use response_schema as it's embedded for simplicity,
    # but the parameter is kept for future flexibility or if we need to revert.
    return OPTIMIZED_SYSTEM_PROMPT.format(
        so_info=so_info,
        tools_description=tools_description,
        history=history
    )

