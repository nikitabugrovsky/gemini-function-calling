# clients/ollama_client.py

import os
import json
from openai import OpenAI
from typing import Dict, List, Optional, Any

from clients.api_client import ApiClient

WEATHER_TOOL_OLLAMA = {
    "name": "get_current_weather",
    "description": "Get the current weather in a given location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA",
            },
        },
        "required": ["location"],
    },
}

OLLAMA_SYSTEM_PROMPT = f"""
You are a helpful assistant that can access a tool to get the weather. Your goal is to assist the user, and that includes deciding when it is appropriate to use your tools.

To use the tool, you MUST respond with a JSON object that specifies the tool name and its arguments. The JSON object must be the only thing in your response, wrapped in ```json tags.

Here is the tool's definition:
{json.dumps(WEATHER_TOOL_OLLAMA, indent=2)}

For example, to get the weather in Paris, you must respond with:
```json
{{
  "tool_call": {{
    "name": "get_current_weather",
    "arguments": {{"location": "Paris"}}
  }}
}}
```

If the user's request is not about weather, or if they are just making a general statement or greeting, you should respond with a natural language message, not a tool call. For example, if the user says "hello" or "how are you", you should respond with a friendly greeting, not a tool call.
"""


class OllamaClient(ApiClient):
    """
    A compliant client for interacting with a local Ollama server that uses a
    prompt-based strategy for function calling.
    """

    def __init__(self, model: str = "gemma3:1b"):
        self.model = model
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # lib stub
        )
        self.history: List[Dict[str, Any]] = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hello! How can I help you today?"},
            {"role": "system", "content": OLLAMA_SYSTEM_PROMPT},
        ]
        self.latest_response_content: Optional[str] = None

    def generate_content(self, user_input: Optional[str], function_execution_result: Optional[dict]) -> None:
        """
        Compliant method to generate a response from the Ollama model.
        It mutates the client's internal state and returns None.
        """
        if user_input:
            self.history.append({"role": "user", "content": user_input})

        if function_execution_result:
            summary_prompt = (
                "You have received the following data from the weather tool: "
                f"{json.dumps(function_execution_result)}. "
                "Use this data to answer the user's request. If the user asked a general question (e.g., 'what is the weather?'), "
                "provide a full summary in a natural language. If the user asked a specific question (e.g., 'what is the temperature?'), "
                "provide a direct answer to that specific question. Use natural language."
            )
            self.history.append({"role": "user", "content": summary_prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            temperature=0,
        )

        self.latest_response_content = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": self.latest_response_content})

    def get_function_call(self) -> Optional[Dict[str, Any]]:
        """
        Compliant method to parse the latest response for a JSON tool call.
        Returns a dictionary with 'name' and 'arguments', or None.
        """
        if not self.latest_response_content:
            return None

        content = self.latest_response_content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()

        try:
            parsed_content = json.loads(content)
            tool_call = parsed_content.get("tool_call")

            if (
                tool_call
                and isinstance(tool_call, dict)
                and "name" in tool_call
                and "arguments" in tool_call
            ):
                return {"name": tool_call["name"], "arguments": tool_call["arguments"]}

        except (json.JSONDecodeError, AttributeError):
            pass

        return None

    def get_text_response(self) -> Optional[str]:
        """
        Compliant method to return the text response if no tool was called.
        """
        if self.latest_response_content:
            if not self.get_function_call():
                return self.latest_response_content
        return None
