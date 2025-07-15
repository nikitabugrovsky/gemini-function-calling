# /// script
# dependencies = [
#   "google-genai",
#   "requests",
# ]
# ///

from google import genai
from google.genai import types

import os
import requests
import urllib.parse

MODEL = "gemini-2.0-flash-lite"

WEATHER_TOOL = {
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

WEATHER_TOOL_INSTRUCTIONS ="\
    Here are the instructions that should be followed when get_current_temperature is invoked: \
    1. Only city name should be taken as a parameter for function invocation.\
    For e.g. New York, USA should become New York\
    2. Abbreviations should be expanded. For e.g. NY should become New York.\
    3. City nicknames should be desyphered into real names. Do not request to clarify, assume instead.\
    For e.g. Big Apple should become New York.\
    4. Cities are not limited to a particular country but rather to the whole world.\
    For e.g. Eternal City should become Rome.\
    5. Cities that have St. in their name should translate to Saint.\
    For e.g. St. Petersburg should become Saint Petersburg.\
    6. When asked about weather assume that you've been asked about temperature.\
    For e.g. What's the weather in Karachi? really means: What's the temperature in Karachi.\
    "

def _get_location_coordinates(location):
    """Gets the coordinates for a given location."""
    url = "https://geocode.maps.co/search?"
    params = {"city": location}
    api_key = os.environ.get("GEOCODE_API_KEY")
    if api_key:
            params["api_key"] = api_key
    geocode_url = url + urllib.parse.urlencode(params)
    geocode_response = requests.get(geocode_url)
    geocode_response.raise_for_status()
    geocode_data = geocode_response.json()
    if not geocode_data:
        return {"error": "Could not find location: no geocode_data"}

    latitude = geocode_data[0]["lat"]
    longitude = geocode_data[0]["lon"]

    return latitude, longitude

def _get_location_temperature(latitude, longitude):
    """Gets the current temperature for a given latitude & longtitude."""
    url = "https://api.open-meteo.com/v1/forecast?"
    params = {"latitude": latitude, "longitude": longitude, "current_weather": "true"}
    open_meteo_url = url + urllib.parse.urlencode(params)
    response = requests.get(open_meteo_url)
    response.raise_for_status()
    data = response.json()

    if "current_weather" in data:
        return {"temperature": data["current_weather"]["temperature"]}
    else:
        return {"error": "Could not get weather data"}

def get_current_temperature(location):
    """Gets the current temperature for a given location."""
    if not location:
        return {"error": "Could not find location: model did not provide location"}
    latitude, longitude = _get_location_coordinates(location)
    temperature = _get_location_temperature(latitude, longitude)

    return temperature

def main():
    """Executes the flow."""

    client = genai.Client()
    tools = types.Tool(function_declarations=[WEATHER_TOOL])
    config = types.GenerateContentConfig(tools=[tools],
        system_instruction=WEATHER_TOOL_INSTRUCTIONS
    )

    print("Gemini Chatbot d[o_0]b (type 'exit' to quit)")
    print("=" * 40)

    while True:
        user_input = input("\nYou:\n").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        response = client.models.generate_content(
            model=MODEL,
            contents=user_input,
            config=config,
        )
        function_call = response.candidates[0].content.parts[0].function_call
        if function_call:
            result = get_current_temperature(**function_call.args)
            chatbot_message = f"""
                I am going to call {function_call.name} function
                Function description: {WEATHER_TOOL.get("description")}
                {("-" * 45)}
                Function arguments: {function_call.args}
                {("-" * 45)}
                Function execution result: {result}
            """
        else:
            chatbot_message = f"""
                No function call found in the response.
                {("-" * 45)}
                Model response: {response.text}
            """

        msg_lines = chatbot_message.splitlines()
        trimmed_msg = [line.lstrip() for line in msg_lines]
        trimmed_chatbot_message = '\n'.join(trimmed_msg)

        print(f"d[o_0]b: {trimmed_chatbot_message}")

if __name__ == "__main__":
    main()
