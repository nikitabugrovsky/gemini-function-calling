# /// script
# dependencies = [
#   "google-genai",
#   "requests",
# ]
# ///

from google import genai
from google.genai import types
from tools.weather_tool import get_current_temperature, WEATHER_TOOL_INSTRUCTIONS

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
        user_input = input("You: ").strip()
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
