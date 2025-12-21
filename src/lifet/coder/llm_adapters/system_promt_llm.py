from typing import Optional

def generate_system_prompt_llm(
    so_info: str,
    tools_description: str,
    history: str,
    agent_persona: Optional[str] = None,
    katas_rules: Optional[str] = None
) -> str:
    """
    Generates the system prompt with dynamic data, including persona and rules.

    Args:
        so_info: Information about the operating system.
        tools_description: Description of available tools.
        history: The conversation history.
        agent_persona: The persona defining the agent's behavior.
        katas_rules: Specific rules for coding or tasks.

    Returns:
        str: The complete system prompt with injected values.
    """
    
    # Base prompt structure
    prompt_parts = [
        "**CRITICAL:** Your output MUST be a single, raw JSON object. No markdown, no commentary.",
        "\n**JSON STRUCTURE:**",
        """{{
    "reasoning": "Your thought process. Be concise.",
    "response": "Your message to the user.",
    "tool_calls": [{{ "tool_name": "tool_name", "arguments": {{"arg": "value"}} }}],
    "task_end": boolean
}}""",
        "\n**FIELD GUIDE:**",
        "- `reasoning`: Brief analysis of the user's request and your plan.",
        "- `response`: A clear, helpful message for the user.",
        "- `tool_calls`: A list of tools to execute. Can be empty.",
        "- `task_end`: `true` if the task is fully complete, `false` if you need to continue. Set to `true` on final success or unrecoverable failure. Set to `false` if you are calling a tool and need to see the result.",
    ]

    prompt_parts.extend([
        "\n**TASK COMPLETION GUIDE:**",
        "1. **Gather Information:** Use tools like `ReadFileTool` and `ListFilesTool` to understand the current state of the codebase.",
        "2. **Avoid Repetition:** Do not read the same file multiple times unless you have a specific reason.",
        "3. **Perform Final Action:** Once you have enough information, perform the main action required by the user (e.g., using `WriteFileTool`).",
        "4. **Conclude:** After performing the final action, set `task_end` to `true`."
    ])

    if agent_persona:
        prompt_parts.extend([
            "\n[AGENT BEHAVIOR]",
            agent_persona
        ])

    if katas_rules:
        prompt_parts.extend([
            "\n[CODING RULES & KATAS]",
            katas_rules
        ])

    prompt_parts.extend([
        "\n[SYSTEM INFO]",
        so_info,
        "\n[AVAILABLE TOOLS]",
        tools_description
    ])

    # Add shell tool guide if shell tool is available
    if "ShellTool" in tools_description:
        prompt_parts.extend([
            "\n**SHELLTOOL GUIDE:**",
            "For complex, multi-line shell commands or Python scripts, use a temporary file to avoid JSON escape errors.",
            "\nExample:",
            """{{
    "tool_calls": [{{
        "tool_name": "ShellTool",
        "arguments": {{"command": "python -c 'import os; print(os.getcwd())'"}}
    }}]
}}""",
            "For simple commands, you can call them directly."
        ])

    prompt_parts.extend([
        "\n[CONVERSATION HISTORY]",
        history
    ])

    return "\n".join(prompt_parts)

