# clients/openai_client.py
from openai import OpenAI
import os
import json
from typing import Optional
from collections import deque

from clients.api_client import ApiClient
from tools.weather_tool import WEATHER_TOOL_INSTRUCTIONS

CONVERSATION_WINDOW_SIZE = 10

WEATHER_TOOL_OPENAI = {
    "type": "function",
    "function": {
        "name": "get_current_weather",
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
        self.messages = deque(maxlen=CONVERSATION_WINDOW_SIZE)
        self.last_response_message = None

    def generate_content(self, user_input: Optional[str], function_execution_result: Optional[dict]) -> None:
        if user_input:
            self.messages.append({"role": "user", "content": user_input})

        if function_execution_result:
            tool_call_id = self.get_function_call()['id']
            self.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": self.get_function_call()['name'],
                    "content": str(function_execution_result),
                }
            )

        messages_to_send = [self.system_message] + list(self.messages)

        self._last_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages_to_send,
            tools=[WEATHER_TOOL_OPENAI],
            tool_choice="auto",
        )
        self.last_response_message = self._last_response.choices[0].message
        if self.last_response_message:
            self.messages.append(self.last_response_message)


    def get_text_response(self) -> str:
        if self.last_response_message and self.last_response_message.content:
            return self.last_response_message.content
        return ""

    def get_function_call(self) -> dict:
        if self.last_response_message and self.last_response_message.tool_calls:
            tc = self.last_response_message.tool_calls[0]
            return {
                "id": tc.id,
                "name": tc.function.name,
                "arguments": json.loads(tc.function.arguments),
                "description": "Function call requested by the model."
            }
        return {}
