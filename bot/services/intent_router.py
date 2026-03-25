"""
Intent router for natural language queries.

This module handles the tool calling loop:
1. Receive user message
2. Send to LLM with tool definitions
3. Execute tool calls
4. Feed results back to LLM
5. Return final answer
"""

import json
import sys
from typing import Optional

from services.lms_api import LmsApiClient
from services.llm_client import LlmClient, ToolsExecutor


# System prompt for the LLM
SYSTEM_PROMPT = """You are an assistant for a university LMS (Learning Management System). 
You have access to backend API tools that provide data about labs, students, scores, and analytics.

Your job is to:
1. Understand the user's question
2. Call the appropriate tools to get the data
3. Analyze the results
4. Provide a clear, helpful answer based on the actual data

Available tools:
- get_items(): Get list of all labs and tasks. Use this when user asks about available labs or tasks.
- get_learners(): Get enrolled students and groups. Use when user asks about enrollment or number of students.
- get_scores(lab: str): Get score distribution (4 buckets) for a specific lab.
- get_pass_rates(lab: str): Get per-task average scores and attempt counts for a lab. Use when user asks about pass rates, scores, or how students performed.
- get_timeline(lab: str): Get submissions per day for a lab.
- get_groups(lab: str): Get per-group scores and student counts. Use when user asks about group performance or compares groups.
- get_top_learners(lab: str, limit: int): Get top N learners by score. Use when user asks about best students or leaderboard.
- get_completion_rate(lab: str): Get completion rate percentage for a lab.
- trigger_sync(): Refresh data from autochecker.

Important rules:
- ALWAYS call tools to get real data before answering
- If you need to compare labs, first call get_items() to get all lab IDs, then call get_pass_rates() for ALL labs in parallel (list all tool calls at once)
- When you see a lab number like "lab 4" or "lab-04", use it as the lab parameter (e.g., "lab-04")
- If the user's message is a greeting or gibberish, respond helpfully without calling tools
- After calling tools, analyze the results and provide specific numbers and names from the data

EFFICIENCY TIP: When you need data from multiple labs, call ALL of them at once in a single batch. For example, if you need pass rates for all labs, call get_pass_rates for lab-01, lab-02, lab-03, etc. all in the same response. The system will execute them in parallel.

Response format:
- Be specific: include actual lab names, numbers, percentages, and counts from the data
- Don't say "I don't have access" - you have the tools to get the data
- If the data shows a clear answer (e.g., lowest pass rate), state it directly with the number
"""


def get_tool_definitions() -> list[dict]:
    """Return tool definitions for the LLM."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get list of all labs and tasks in the system",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get enrolled students and their groups",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution (4 buckets) for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submissions per day for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return, e.g. 5, 10",
                            "default": 10,
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Refresh data from autochecker",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


def normalize_lab_id(value: str) -> str:
    """Normalize lab ID to standard format (e.g., 'lab-01')."""
    value = value.lower().strip()
    # Handle various formats: "lab 4", "lab4", "lab-4", "lab-04"
    if value.startswith("lab"):
        # Extract number
        import re

        match = re.search(r"(\d+)", value)
        if match:
            num = int(match.group(1))
            return f"lab-{num:02d}"
    return value


class IntentRouter:
    """Router that uses LLM to interpret natural language queries."""

    def __init__(
        self,
        llm_client: LlmClient,
        api_client: LmsApiClient,
        debug: bool = False,
    ):
        self.llm = llm_client
        self.api = api_client
        self.debug = debug
        self.tools_executor = self._create_tools_executor()

    def _create_tools_executor(self) -> ToolsExecutor:
        """Create and configure the tools executor with all backend tools."""
        executor = ToolsExecutor()

        # Register all 9 tools
        executor.register("get_items", self.api.get_items)
        executor.register("get_learners", self.api.get_learners)

        # Wrap methods to normalize lab IDs
        def get_scores(lab: Optional[str] = None):
            return self.api.get_scores(lab=normalize_lab_id(lab) if lab else None)

        def get_pass_rates(lab: Optional[str] = None):
            return self.api.get_pass_rates(lab=normalize_lab_id(lab) if lab else None)

        def get_timeline(lab: Optional[str] = None):
            return self.api.get_timeline(lab=normalize_lab_id(lab) if lab else None)

        def get_groups(lab: Optional[str] = None):
            return self.api.get_groups(lab=normalize_lab_id(lab) if lab else None)

        def get_top_learners(lab: Optional[str] = None, limit: int = 10):
            return self.api.get_top_learners(
                lab=normalize_lab_id(lab) if lab else None, limit=limit
            )

        def get_completion_rate(lab: Optional[str] = None):
            return self.api.get_completion_rate(
                lab=normalize_lab_id(lab) if lab else None
            )

        executor.register("get_scores", get_scores)
        executor.register("get_pass_rates", get_pass_rates)
        executor.register("get_timeline", get_timeline)
        executor.register("get_groups", get_groups)
        executor.register("get_top_learners", get_top_learners)
        executor.register("get_completion_rate", get_completion_rate)
        executor.register("trigger_sync", self.api.trigger_sync)

        return executor

    def route(self, message: str) -> str:
        """
        Process a natural language message and return a response.

        This implements the tool calling loop:
        1. Send message to LLM with tool definitions
        2. If LLM calls tools, execute them and feed results back
        3. Continue until LLM produces final answer
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        tool_definitions = get_tool_definitions()
        max_iterations = 15  # Allow more iterations for multi-step queries

        for iteration in range(max_iterations):
            if self.debug:
                print(f"[iteration {iteration}] Processing...", file=sys.stderr)

            try:
                response_text, tool_calls = self.llm.chat(
                    messages, tools=tool_definitions, debug=self.debug
                )
            except Exception as e:
                if self.debug:
                    print(f"[LLM error] {e}", file=sys.stderr)
                return f"LLM error: {e}"

            # If no tool calls, LLM has a final answer
            if not tool_calls:
                if self.debug:
                    print(f"[iteration {iteration}] Final answer received", file=sys.stderr)
                return response_text

            # Execute all tool calls (they are independent, so we can batch them)
            if self.debug:
                print(f"[batch] Executing {len(tool_calls)} tool calls in parallel", file=sys.stderr)

            tool_results = []
            for tc in tool_calls:
                result = self.llm.execute_tool_call(
                    tc, self.tools_executor, debug=self.debug
                )
                tool_results.append(result)

            # Feed tool results back to LLM
            if self.debug:
                print(
                    f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM",
                    file=sys.stderr,
                )

            messages.append({"role": "assistant", "tool_calls": tool_calls})
            for result in tool_results:
                messages.append(result)

        # If we get here, we hit max iterations
        if self.debug:
            print(f"[warning] Hit max iterations ({max_iterations})", file=sys.stderr)
        return "I'm having trouble processing this query. Please try rephrasing."


def handle_natural_query(message: str, debug: bool = False) -> str:
    """
    Handle a natural language query.

    This is the main entry point for the intent router.
    It creates clients from config and routes the message.
    """
    from config import load_config

    config = load_config()

    # Validate config
    if not config.llm_api_key or not config.llm_api_base_url:
        return "LLM configuration not set. Please check .env.bot.secret"

    if not config.lms_api_key or not config.lms_api_base_url:
        return "LMS API configuration not set. Please check .env.bot.secret"

    # Create clients
    llm_client = LlmClient(
        api_key=config.llm_api_key,
        base_url=config.llm_api_base_url,
        model=config.llm_api_model,
    )

    api_client = LmsApiClient(
        base_url=config.lms_api_base_url,
        api_key=config.lms_api_key,
    )

    # Create router and process message
    router = IntentRouter(llm_client, api_client, debug=debug)
    return router.route(message)
