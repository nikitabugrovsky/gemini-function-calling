# clients/genai_client.py
import os
from typing import Dict, Any, Optional
from collections import deque

from google.genai.client import Client
from google.genai.types import (
    Tool,
    Content,
    Part,
    FunctionResponse,
    GenerateContentConfig,
)

from clients.api_client import ApiClient
from tools.weather_tool import WEATHER_TOOL_INSTRUCTIONS

CONVERSATION_WINDOW_SIZE = 10

WEATHER_TOOL_GENAI = {
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


class GenAIClient(ApiClient):
    """API client for the google-genai library."""

    def __init__(self, model: str):
        super().__init__(model)
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client = Client(api_key=api_key)
        self.history = deque(maxlen=CONVERSATION_WINDOW_SIZE)
        tool = Tool(function_declarations=[WEATHER_TOOL_GENAI])
        self.config = GenerateContentConfig(
            tools=[tool],
            system_instruction=WEATHER_TOOL_INSTRUCTIONS
        )

    def generate_content(
            self, user_input: Optional[str], function_execution_result: Optional[dict] = None
    ) -> None:
        if function_execution_result:
            function_call = self.get_function_call()
            if not function_call:
                return

            function_name = function_call.get("name")
            function_response = FunctionResponse(
                name=function_name,
                response={"result": function_execution_result},
            )

            if self._last_response and self._last_response.candidates:
                 self.history.append(self._last_response.candidates[0].content)

            self.history.append(
                Content(
                    parts=[Part(function_response=function_response)],
                    role="tool",
                )
            )
        elif user_input:
            self.history.append(Content(parts=[Part(text=user_input)], role="user"))

        contents_to_send = list(self.history)

        self._last_response = self.client.models.generate_content(
            model=self.model,
            contents=contents_to_send,
            config=self.config,
        )

        part = self._last_response.candidates[0].content.parts[0]
        if not part.function_call:
             self.history.append(self._last_response.candidates[0].content)


    def get_function_call(self) -> Optional[Dict[str, Any]]:
        if self._last_response and self._last_response.candidates:
            part = self._last_response.candidates[0].content.parts[0]
            if part.function_call:
                return {
                    "name": part.function_call.name,
                    "arguments": dict(part.function_call.args),
                    "description": WEATHER_TOOL_GENAI.get("description"),
                }
        return None

    def get_text_response(self) -> Optional[str]:
        if (
                self._last_response
                and self._last_response.candidates
                and self._last_response.candidates[0].content.parts
                and self._last_response.candidates[0].content.parts[0].text
        ):
            return self._last_response.candidates[0].content.parts[0].text
        return ""
