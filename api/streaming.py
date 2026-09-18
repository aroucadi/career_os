"""
Vercel AI SDK Data Stream Protocol Helpers
==========================================
Encodes streaming chunks according to the Vercel AI SDK UI Stream specification:
- 0:"text_delta"\n : Assistant message content streaming token
- b:{"toolCallId": "...", "toolName": "...", "args": {...}}\n : Tool call started (triggers React widget)
- c:{"toolCallId": "...", "result": {...}}\n : Tool call completed
- d:{"finishReason": "stop"}\n : Completion stream event
"""

import json
from typing import Any, Dict, Optional

def format_text_delta(token: str) -> str:
    """Formats a text token as a Vercel AI SDK text part."""
    # Prefix '0:' followed by JSON-encoded string and newline
    return f"0:{json.dumps(token)}\n"

def format_tool_call(tool_call_id: str, tool_name: str, args: Dict[str, Any]) -> str:
    """Formats a tool invocation part triggering an atomic UI component on Next.js."""
    payload = {
        "toolCallId": tool_call_id,
        "toolName": tool_name,
        "args": args
    }
    return f"9:{json.dumps(payload)}\n"

def format_tool_result(tool_call_id: str, result: Dict[str, Any]) -> str:
    """Formats a tool result part."""
    payload = {
        "toolCallId": tool_call_id,
        "result": result
    }
    return f"a:{json.dumps(payload)}\n"

def format_finish_message(finish_reason: str = "stop") -> str:
    """Formats stream completion indicator."""
    payload = {
        "finishReason": finish_reason,
        "usage": {"promptTokens": 0, "completionTokens": 0}
    }
    return f"d:{json.dumps(payload)}\n"
