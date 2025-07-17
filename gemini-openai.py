# /// script
# dependencies = [
#   "openai",
#   "requests",
# ]
# ///

from openai import OpenAI
import os
from tools.weather_tool import get_current_temperature, WEATHER_TOOL_INSTRUCTIONS

MODEL = "gemini-2.0-flash-lite"

WEATHER_TOOL = {
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

def main():
    """Executes the flow."""

    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/",
        api_key=os.environ["GEMINI_API_KEY"],
    )

    print("Gemini Chatbot d[o_0]b (type 'exit' to quit)")
    print("=" * 40)

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
            {
                    "role": "system",
                    "content": WEATHER_TOOL_INSTRUCTIONS,
                },
                {
                    "role": "user",
                    "content": user_input,
                }
            ],
            tools=[WEATHER_TOOL],
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            result = get_current_temperature(**eval(tool_calls[0].function.arguments))
            chatbot_message = f"""
                I am going to call {tool_calls[0].function.name} function
                Function description: {WEATHER_TOOL["function"]["description"]}
                {("-" * 45)}
                Function arguments: {tool_calls[0].function.arguments}
                {("-" * 45)}
                Function execution result: {result}
            """
        else:
            chatbot_message = f"""
                No function call found in the response.
                {("-" * 45)}
                Model response: {response_message.content}
            """

        msg_lines = chatbot_message.splitlines()
        trimmed_msg = [line.lstrip() for line in msg_lines]
        trimmed_chatbot_message = '\n'.join(trimmed_msg)

        print(f"d[o_0]b: {trimmed_chatbot_message}")

if __name__ == "__main__":
    main()
