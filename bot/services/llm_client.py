"""
LLM client with tool calling support.

This client handles the conversation loop:
1. Send user message + tool definitions to LLM
2. LLM returns tool calls
3. Execute tools and feed results back
4. LLM produces final answer
"""

import json
import sys
from typing import Optional

import httpx


class LlmClient:
    """Client for LLM API with tool calling support."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        debug: bool = False,
    ) -> tuple[str, list[dict]]:
        """
        Send a chat request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions
            debug: If True, print debug info to stderr

        Returns:
            Tuple of (response_text, list_of_tool_calls)
        """
        payload = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            response = self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                print(
                    "LLM error: HTTP 401 - Token expired. Restart the Qwen proxy:",
                    file=sys.stderr,
                )
                print(
                    "  cd ~/qwen-code-oai-proxy && docker compose restart",
                    file=sys.stderr,
                )
            else:
                print(f"LLM HTTP error: {e}", file=sys.stderr)
            raise

        choice = data["choices"][0]
        message = choice["message"]
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])

        if debug and tool_calls:
            for tc in tool_calls:
                func = tc["function"]
                args = json.loads(func.get("arguments", "{}"))
                print(f"[tool] LLM called: {func['name']}({args})", file=sys.stderr)

        return content, tool_calls

    def execute_tool_call(
        self, tool_call: dict, tools_executor: "ToolsExecutor", debug: bool = False
    ) -> dict:
        """
        Execute a single tool call and return the result.

        Args:
            tool_call: Tool call dict from LLM
            tools_executor: Executor that maps tool names to functions
            debug: If True, print debug info to stderr

        Returns:
            Dict with tool call result
        """
        func = tool_call["function"]
        name = func["name"]
        arguments = json.loads(func.get("arguments", "{}"))

        try:
            result = tools_executor.execute(name, arguments)
            if debug:
                # Print summary of result
                if isinstance(result, list):
                    print(
                        f"[tool] Result: {len(result)} items",
                        file=sys.stderr,
                    )
                elif isinstance(result, dict):
                    keys = ", ".join(str(k) for k in result.keys()[:5])
                    print(f"[tool] Result: dict with keys: {keys}", file=sys.stderr)
                else:
                    print(f"[tool] Result: {result}", file=sys.stderr)
            return {
                "tool_call_id": tool_call["id"],
                "role": "tool",
                "name": name,
                "content": json.dumps(result, ensure_ascii=False, default=str),
            }
        except Exception as e:
            if debug:
                print(f"[tool] Error executing {name}: {e}", file=sys.stderr)
            return {
                "tool_call_id": tool_call["id"],
                "role": "tool",
                "name": name,
                "content": f"Error: {e}",
            }


class ToolsExecutor:
    """Executor that maps tool names to callable functions."""

    def __init__(self):
        self._tools = {}

    def register(self, name: str, func):
        """Register a tool function."""
        self._tools[name] = func

    def execute(self, name: str, arguments: dict):
        """Execute a tool by name with given arguments."""
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name](**arguments)

    def get_tools(self) -> list[str]:
        """Get list of registered tool names."""
        return list(self._tools.keys())
