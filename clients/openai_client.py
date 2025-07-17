# clients/openai_client.py
from openai import OpenAI
import os
import json
from typing import Dict, Any, Optional

from clients.api_client import ApiClient
from tools.weather_tool import WEATHER_TOOL_INSTRUCTIONS

WEATHER_TOOL_OPENAI = {
    "type": "function",
    "function": {
        "name": "get_current_temperature",
        "description": "🌡️Gets the current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name, e.g. New York",
                },
            },
            "required": ["location"],
        },
    }
}

class OpenAIClient(ApiClient):
    """API client for the openai library."""

    def __init__(self, model: str):
        super().__init__(model)
        self.client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/",
            api_key=os.environ["GEMINI_API_KEY"],
        )
        self.system_message = {"role": "system", "content": WEATHER_TOOL_INSTRUCTIONS}

    def generate_content(self, user_input: str) -> None:
        messages = [self.system_message, {"role": "user", "content": user_input}]
        self._last_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=[WEATHER_TOOL_OPENAI],
            tool_choice="auto",
        )

    def get_function_call(self) -> Optional[Dict[str, Any]]:
        if self._last_response:
            response_message = self._last_response.choices[0].message
            if response_message.tool_calls:
                tool_call = response_message.tool_calls[0].function
                return {
                    "name": tool_call.name,
                    "arguments": json.loads(tool_call.arguments),
                    "description": WEATHER_TOOL_OPENAI["function"]["description"]
                }
        return None

    def get_text_response(self) -> Optional[str]:
        if self._last_response:
            return self._last_response.choices[0].message.content
        return None
