# clients/genai_client.py
from google import genai
from google.genai import types
from typing import Dict, Any, Optional

from clients.api_client import ApiClient
from tools.weather_tool import WEATHER_TOOL_INSTRUCTIONS

WEATHER_TOOL_GENAI = {
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

class GenAIClient(ApiClient):
    """API client for the google-genai library."""

    def __init__(self, model: str):
        super().__init__(model)
        self.client = genai.Client()
        tool = types.Tool(function_declarations=[WEATHER_TOOL_GENAI])
        self.config = types.GenerateContentConfig(
            tools=[tool],
            system_instruction=WEATHER_TOOL_INSTRUCTIONS
        )

    def generate_content(self, user_input: str) -> None:
        self._last_response = self.client.models.generate_content(
            model=self.model,
            contents=user_input,
            config=self.config,
        )

    def get_function_call(self) -> Optional[Dict[str, Any]]:
        if self._last_response:
            part = self._last_response.candidates[0].content.parts[0]
            if part.function_call:
                return {
                    "name": part.function_call.name,
                    "arguments": dict(part.function_call.args),
                    "description": WEATHER_TOOL_GENAI.get("description")
                }
        return None

    def get_text_response(self) -> Optional[str]:
        if self._last_response:
            return self._last_response.text
        return None
