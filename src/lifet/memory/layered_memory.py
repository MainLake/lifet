from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from lifet.memory.memory_protocol import MemoryProtocol, MemoryInteraction

class LayeredMemory(MemoryProtocol):
    """
    Layered memory system to maintain relevant context without exceeding token limits.
    """
    
    def __init__(self, max_recent_messages: int = 10):
        self.max_recent_messages = max_recent_messages
        
        # Layer 1: High-level summary (always included)
        self.summary = {
            "project_structure": {},
            "current_task": "Waiting for user input",
            "completed_tasks": [],
            "key_decisions": []
        }
        
        # Layer 2: Recent messages (sliding window)
        self.recent_messages: List[Dict[str, Any]] = []
        
        # Layer 3: Important tool results (indexed)
        self.tool_results_index: Dict[str, Dict[str, Any]] = {}
        
        # Layer 4: Full history (for analysis/debugging)
        self.full_history: List[Dict[str, Any]] = []
    
    def save_memory(self, interaction: MemoryInteraction):
        """
        Saves a single interaction to the memory.
        Note: The original protocol uses MemoryInteraction, but this class 
        internally uses a dictionary structure for richer metadata. 
        We adapt the simple interaction to our internal structure.
        """
        # Create a richer object for our internal storage
        # If the interaction content is JSON (from tool results), we might want to parse it,
        # but for now we treat it as string as per protocol.
        
        rich_interaction = {
            "timestamp": datetime.now().isoformat(),
            "role": interaction.role,
            "content": interaction.content
        }
        
        # Update layers
        self._update_layers(rich_interaction)
        
    def _update_layers(self, interaction: Dict[str, Any]):
        """Updates all memory layers based on the new interaction."""
        
        # Update Layer 2: Recent messages
        self.recent_messages.append(interaction)
        if len(self.recent_messages) > self.max_recent_messages:
            self.recent_messages.pop(0)
            
        # Update Layer 4: Full history
        self.full_history.append(interaction)
        
        # Update Layer 1 & 3 based on content analysis
        # (Simplified logic: in a real scenario we'd parse the content more deeply)
        self._analyze_content_for_summary(interaction)

    def _analyze_content_for_summary(self, interaction: Dict[str, Any]):
        """
        Analyzes content to update summary and tool index.
        This is a heuristic approach.
        """
        content = interaction["content"]
        role = interaction["role"]
        
        # Update current task if user sends a new request
        if role == "user":
            # Heuristic: the last user message is likely the current sub-task
            self.summary["current_task"] = content[:200]  # Truncate if too long
            
        # Index tool results if they look file-related
        if role == "tool" or role == "system": # system sometimes acts as tool output/error
             # Trying to identify if this is a file reading result
             # This is tricky without structured tool output in the raw string, 
             # but we can look for keywords if we want to be smart.
             # For now, let's just keep the sliding window valid.
             pass

    def get_memory(self) -> str:
        """
        Generates the optimized context for the LLM.
        """
        context_parts = []
        
        # Part 1: High-level Summary
        context_parts.append("# Project Context")
        context_parts.append(f"Current Task: {self.summary['current_task']}")
        
        if self.summary["completed_tasks"]:
            context_parts.append("\n## Recently Completed Tasks:")
            for task in self.summary["completed_tasks"][-3:]:
                context_parts.append(f"- {task['task']}")
                
        # Part 2: Recent Interactions (Sliding Window)
        context_parts.append("\n# Recent History")
        for msg in self.recent_messages:
            role_header = f"[{msg['role'].upper()}]"
            if msg['role'] == "tool":
                role_header = "[TOOL_RESULT]"
            
            # Truncate very long tool outputs in the view (they are still in full history)
            content = msg['content']
            if len(content) > 2000:
                content = content[:1000] + "\n...[content truncated]...\n" + content[-1000:]
                
            context_parts.append(f"{role_header}\n{content}")
            
        return "\n\n".join(context_parts)

    # Extended method not in protocol but useful for the Coder to call if it knows about LayeredMemory
    def add_structured_interaction(self, 
                       user_request: str,
                       llm_reasoning: str, 
                       llm_response: str,
                       tool_calls: List[Dict],
                       tool_results: List[Dict]):
        """
        Advanced method to add a full cycle of interaction with structured data.
        This allows much better summary updates.
        """
        interaction_group = {
            "timestamp": datetime.now().isoformat(),
            "user_request": user_request,
            "llm_reasoning": llm_reasoning,
            "llm_response": llm_response,
            "tool_calls": tool_calls,
            "tool_results": tool_results
        }
        
        # 1. Save user request
        self.save_memory(MemoryInteraction(role="user", content=user_request))
        
        # 2. Save assistant response logic
        assistant_content = []
        if llm_reasoning:
            assistant_content.append(f"Thought: {llm_reasoning}")
        if tool_calls:
            assistant_content.append(f"Action: Call tool(s): {json.dumps(tool_calls)}")
        if llm_response:
            assistant_content.append(f"Response: {llm_response}")
            
        self.save_memory(MemoryInteraction(role="assistant", content=" ".join(assistant_content)))
        
        # 3. Save Tool Results & Index them
        for tc, tr in zip(tool_calls, tool_results):
            tool_name = tc.get("tool_name", "unknown")
            args = tc.get("arguments", {})
            result_str = str(tr.get("result", ""))
            
            # Indexing logic
            if any(cmd in str(args) for cmd in ["cat", "read", "ls", "find", "grep"]):
                 key = f"{tool_name}:{str(args)}"
                 self.tool_results_index[key] = {
                     "result": result_str[:500] + ("..." if len(result_str)>500 else ""),
                     "timestamp": datetime.now().isoformat()
                 }
            
            self.save_memory(MemoryInteraction(role="tool", content=f"Result of {tool_name}: {result_str}"))

        # Update summary more intelligently
        if "completed" in llm_reasoning.lower() or "finished" in llm_reasoning.lower():
             self.summary["completed_tasks"].append({
                "task": user_request,
                "completed_at": datetime.now().isoformat()
            })
